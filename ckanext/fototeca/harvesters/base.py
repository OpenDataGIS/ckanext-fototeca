import logging
import json
import re
import hashlib
from past.builtins import basestring
import pandas as pd
import dateutil

from ckan import logic
from ckan.logic import NotFound, get_action
import ckan.plugins as p
import ckan.model as model
from ckantoolkit import config
from ckan.model import Session
from ckan.logic.schema import default_create_package_schema
from ckan.lib.navl.validators import ignore_missing, ignore

from ckanext.harvest.logic.schema import unicode_safe
from ckanext.harvest.model import HarvestObject, HarvestObjectExtra

from ckanext.schemingdcat.harvesters.base import SchemingDCATHarvester
from ckanext.schemingdcat.interfaces import ISchemingDCATHarvester

from ckanext.fototeca.interfaces import ISQLHarvester
from ckanext.fototeca.lib.routing_sql.routing_pg import routingPG
from ckanext.fototeca.lib.sql_field_mapping import SqlFieldMappingValidator as FieldMappingValidator

log = logging.getLogger(__name__)


class SQLHarvester(SchemingDCATHarvester):
    """
    A custom harvester for harvesting metadata using the Fototeca extension.

    It extends the base `SchemingDCATHarvester` class provided by CKAN's schemingdcat extension.
    """

    def info(self):
        return {
            'name': 'fototeca_sql_harvester',
            'title': 'SQL Database Harvester',
            'description': 'An SQL database harvester for CKAN'
        }

    _readme = "https://github.com/OpenDataGIS/ckanext-fototeca?tab=readme-ov-file"
    _database_types_supported = {
        'postgres': {
            'name': 'postgres',
            'title': 'PostgreSQL',
            'active': True,
        },
        'sqlite': {
            'name': 'sqlite',
            'title': 'SQLite',
            'active': False
        }
    }

    _credentials = None
    data = None
    config = None
    _field_mapping_required = {
        "dataset_field_mapping": True,
        "distribution_field_mapping": False,
        "datadictionary_field_mapping": False,
    }

    def gather_stage(self, harvest_job):
        
        source_url = harvest_job.source.url

        log.debug('In gater_stage with database: %s', source_url)
        
        content_dict = {}
        self._names_taken = []
        
        # obtener Opciones de configuración
        if harvest_job.source.config:
            self.config = json.loads(harvest_job.source.config)
            database_type = self.config.get("database_type")
            credentials = self.config.get("credentials")
            dataset_field_mapping = self.config.get("dataset_field_mapping")

        ###definición de engines de SQLalchemy
        ##En caso de querer agregar nuevas bases de datos añadirlas con 
        ##elif al condicional
        if database_type == "postgres":
            log.debug("starting database remote schema harvest")
            database = routingPG(credentials['user'],credentials['password'],credentials['host'],credentials['port'],credentials['db'])
        else:
            raise ValueError("unsupported database reached gather stage")
        #
        ###realizar query y obtener los valores de la base de datos
        #log.debug(dataset_field_mapping)
        #with engine.connect() as conn:
        #    query = self._create_query(dataset_field_mapping['fields'],dataset_field_mapping['p_key'])
        #    log.debug(query)
        #    result = conn.execute(text(query))
        #    dataList = result.fetchall()

        keys = []
        values = []

        log.debug(dataset_field_mapping)

        for key, value in dataset_field_mapping.items():
            keys.append(str(key))
            values.append(str(value["field_name"]))

        dataList = database.get_columns(values)
       
        self.data = pd.DataFrame(data=dataList, columns=keys)
        log.debug(self.data)
        self.data.reset_index() 

        ##TODO implementar validación de esquema

        datasets_to_harvest = {}
        guids_in_harvest = set()
        #guids_in_db = set(guid_to_package_id.keys())

        log.debug("Añadimos dataset a base de datos")
        for index, row in self.data.iterrows():
            print(row)
            try:
                source_dataset = model.Package.get(harvest_job.source.id)
                if 'name' not in row:
                    row['name'] = self._gen_new_name(row['title'])
                while row['name'] in self._names_taken:
                    suffix = sum(name.startswith(row['name'] + '-') for name in self._names_taken) + 1
                    row['name'] = '{}-{}'.format(row['name'], suffix)
                self._names_taken.append(row['name'])

                # Si no hay identificador usar el nombre
                if 'identifier' not in row:
                    row['identifier'] = self._generate_identifier(row)
            except Exception as e:
                self._save_gather_error('Error for the dataset identifier %s [%r]' % (row['identifier'], e), harvest_job)
                continue
        
            #Establecer campos traducidos
            row = self._set_translated_fields(row)

            #Obtener el owner del dataset si existe
            if not row.get('owner_org'):
                if source_dataset.owner_org:
                    row['owner_org'] = source_dataset.owner_org

            if 'extras' not in row:
                row['extras'] = []

            guids_in_harvest.add(row['identifier'])
            datasets_to_harvest[row['identifier']] = row

        log.debug(datasets_to_harvest)
        
        # obtener GUIDs anteriores
        qGuid = \
            model.Session.query(HarvestObject.guid, HarvestObject.package_id) \
            .filter(HarvestObject.current == True) \
            .filter(HarvestObject.harvest_source_id == harvest_job.source.id)
        guid_to_package_id = {}

        for guid, package_id in qGuid:
            guid_to_package_id[guid] = package_id

        guids_in_db = set(guid_to_package_id.keys())

        # Check guids to create/update/delete
        new = guids_in_harvest - guids_in_db
        # Get objects/datasets to delete (ie in the DB but not in the source)
        delete = set(guids_in_db) - set(guids_in_harvest)
        change = guids_in_db & guids_in_harvest

        log.debug('new: %s, delete: %s and change: %s', new, delete, change)

        ##Generamos HarvestObject
        ids = []
        for guid in new:
            log.debug("guid: "+ guid)
            log.debug(datasets_to_harvest.get(guid).to_dict())
            obj = HarvestObject(guid=guid, job=harvest_job, content=json.dumps(datasets_to_harvest.get(guid).to_dict()),
                                extras=[HarvestObjectExtra(key='status', value='new')])
            obj.save()
            ids.append(obj.id)

        for guid in change:
            obj = HarvestObject(guid=guid, job=harvest_job, content=json.dumps(datasets_to_harvest.get(guid).to_dict()),
                                package_id=guid_to_package_id[guid],
                                extras=[HarvestObjectExtra(key='status', value='change')])
            obj.save()
            ids.append(obj.id)
            
        for guid in delete:
            obj = HarvestObject(guid=guid, job=harvest_job, content=json.dumps(datasets_to_harvest.get(guid).to_dict()),
                                package_id=guid_to_package_id[guid],
                                extras=[HarvestObjectExtra(key='status', value='delete')])
            model.Session.query(HarvestObject).\
                  filter_by(guid=guid).\
                  update({'current': False}, False)
            obj.save()
            ids.append(obj.id)

        return ids

    def _create_query(self,fields,p_key):
        fieldsJoined = " ,".join(list(fields.values()))
        log.debug(fieldsJoined)
        p_keyList = list(p_key.items())
        query = "select "+fieldsJoined

        if 'oneTable' not in p_key:
            table1 = ".".join(p_keyList[0][0].split('.')[0:2])
            table2 = ".".join(p_keyList[0][1].split('.')[0:2])
            query += " from "+ table1+ " left join "+table2 +" on "+ p_keyList[0][0] +"="+ p_keyList[0][1]

            for field in p_keyList[1:]:
                table1 = ".".join(field.split[0]('.')[0:2])
                table2 = ".".join(field.split[1]('.')[0:2])
                query += " from "+ table1+ " left join "+table2 +" on "+ field[0] +"="+ field[1]
        else:
            table2 = ".".join(p_keyList[0][1].split('.')[0:2])
            query += " from " + table2
        
        return query

    # TODO: database_p_keys _is_not_db_key
    def _validate_dataset_pkeys(database_type, config_obj):
        database_p_keys = config_obj['database_p_keys']
        log.debug("database_type = "+ database_p_keys)
        if not isinstance(database_p_keys, basestring):
            raise ValueError('database_type must be a string')

        #TODO: Loop over database_p_keys

        config = json.dumps({**config_obj, 'database_type': database_type})
    
        return config

        # if 'database_mapping' in config:
        #     database_mapping = config_obj['database_mapping']

        #     if not isinstance(next(iter(database_mapping)),dict):
        #         ValueError('database_mapping must be a collection of dictionaries')
        #     else:
        #         if 'p_key' in database_mapping:
        #             if not isinstance(database_mapping['p_key'],dict):
        #                 ValueError('p_key must be a dictionary')
        #             else:
        #                 if self._is_not_db_key(next(iter(database_mapping['p_key']))):
        #                     ValueError('wrong "p_key" database field format; should be schema.table.value')
                        
        #             if not isinstance(database_mapping['fields']):
        #                 ValueError('fields must be a dictionary')
        #             else:
        #                 if self._is_not_db_key(next(iter(database_mapping['fields']))):
        #                     ValueError('wrong "fields" database field format; should be schema.table.value')


        # def _is_not_db_key(self, string):
        #     field = string.split('.')

        #     if length(field) != 3:
        #         raise ValueError(f'"The lenght of the field is: {length(field)}"')

    def fetch_stage(self, harvest_object):
    #vacío porque los datos ya estan recopilados en gather_stage
        return True

    #TODO implementar el import stage 
    def import_stage(self, harvest_object):
        """
        Performs the import stage of the SchemingDCATXLSHarvester.

        Args:
            harvest_object (HarvestObject): The harvest object to import.

        Returns:
            bool or str: Returns True if the import is successful, 'unchanged' if the package is unchanged,
                        or False if there is an error during the import.

        Raises:
            None
        """
        log.debug('In SchemingDCATXLSHarvester import_stage')

        harvester_tmp_dict = {}
        context = {
            'model': model,
            'session': model.Session,
            'user': self._get_user_name(),
        }
        
        if not harvest_object:
            log.error('No harvest object received')
            return False   
        
        self._set_config(harvest_object.source.config)
        
        if self.force_import:
            status = 'change'
        else:
            status = self._get_object_extra(harvest_object, 'status')

        # Get the last harvested object (if any)
        previous_object = model.Session.query(HarvestObject) \
                          .filter(HarvestObject.guid==harvest_object.guid) \
                          .filter(HarvestObject.current==True) \
                          .first()

        if status == 'delete':
            override_local_datasets = self.config.get("override_local_datasets", False)
            if override_local_datasets is True:
                # Delete package
                context.update({
                    'ignore_auth': True,
                })
                p.toolkit.get_action('package_delete')(context, {'id': harvest_object.package_id})
                log.info('The override_local_datasets configuration is %s. Package %s deleted with GUID: %s' % (override_local_datasets, harvest_object.package_id, harvest_object.guid))

                return True
            
            else:
                log.info('The override_local_datasets configuration is %s. Package %s not deleted with GUID: %s' % (override_local_datasets, harvest_object.package_id, harvest_object.guid))

                return 'unchanged'

        # Check if harvest object has a non-empty content
        if harvest_object.content is None:
            self._save_object_error('Empty content for object {0}'.format(harvest_object.id),
                                    harvest_object, 'Import')
            return False

        try:
            dataset = json.loads(harvest_object.content)
        except ValueError:
            self._save_object_error('Could not ateutil.parser.parse content for object {0}'.format(harvest_object.id),
                                    harvest_object, 'Import')
            return False

        # Check if the dataset is a harvest source and we are not allowed to harvest it
        if dataset.get('type') == 'harvest' and self.config.get('allow_harvest_datasets', False) is False:
            log.warn('Remote dataset is a harvest source and allow_harvest_datasets is False, ignoring...')
            return True

        dataset = self.modify_package_dict(dataset, harvest_object)

        # Flag previous object as not current anymore
        if previous_object and not self.force_import:
            previous_object.current = False
            previous_object.add()

        # Dataset dict::Update GUID with the identifier from the dataset
        remote_guid = dataset['identifier']
        if remote_guid and harvest_object.guid != remote_guid:
            # First make sure there already aren't current objects
            # with the same guid
            existing_object = model.Session.query(HarvestObject.id) \
                            .filter(HarvestObject.guid==remote_guid) \
                            .filter(HarvestObject.current==True) \
                            .first()
            if existing_object:
                self._save_object_error('Object {0} already has this guid {1}'.format(existing_object.id, remote_guid),
                        harvest_object, 'Import')
                return False

            harvest_object.guid = remote_guid
            harvest_object.add()

        # Assign GUID if not present (i.e. it's a manual import)
        if not harvest_object.guid:
            harvest_object.guid = remote_guid
            harvest_object.add()

        # Update dates
        self._source_date_format = self.config.get('source_date_format', None)
        self._set_basic_dates(dataset)

        harvest_object.metadata_modified_date = dataset['modified']
        harvest_object.add()

        # Build the package dict
        package_dict = self.get_package_dict(harvest_object, context, dataset)
        if not package_dict:
            log.error('No package dict returned, aborting import for object %s' % harvest_object.id)
            return False

        # Create / update the package
        context.update({
           'extras_as_string': True,
           'api_version': '2',
           'return_id_only': True})

        if self._site_user and context['user'] == self._site_user['name']:
            context['ignore_auth'] = True

        # Flag this object as the current one
        harvest_object.current = True
        harvest_object.add()

        if status == 'new':       
            # We need to explicitly provide a package ID based on uuid4 identifier created in gather_stage
            # won't be be able to link the extent to the package.
            package_dict['id'] = package_dict['identifier']

            # before_create interface
            for harvester in p.PluginImplementations(ISchemingDCATHarvester):
                if hasattr(harvester, 'before_create'):
                    err = harvester.before_create(harvest_object, package_dict, self._local_schema, harvester_tmp_dict)
                
                    if err:
                        self._save_object_error(f'before_create error: {err}', harvest_object, 'Import')
                        return False
            
            try:
                result = self._create_or_update_package(
                    package_dict, harvest_object, 
                    package_dict_form='package_show')
                
                # after_create interface
                for harvester in p.PluginImplementations(ISchemingDCATHarvester):
                    if hasattr(harvester, 'after_create'):
                        err = harvester.after_create(harvest_object, package_dict, harvester_tmp_dict)

                        if err:
                            self._save_object_error(f'after_create error: {err}', harvest_object, 'Import')
                            return False

            except p.toolkit.ValidationError as e:
                error_message = ', '.join(f'{k}: {v}' for k, v in e.error_dict.items())
                self._save_object_error(f'Validation Error: {error_message}', harvest_object, 'Import')
                return False

        elif status == 'change':
            # Check if the modified date is more recent
            if not self.force_import and previous_object and dateutil.parser.parse(harvest_object.metadata_modified_date) <= previous_object.metadata_modified_date:
                log.info('Package with GUID: %s unchanged, skipping...' % harvest_object.guid)
                return 'unchanged'
            else:
                log.info("Dataset dates - Harvest date: %s and Previous date: %s", harvest_object.metadata_modified_date, previous_object.metadata_modified_date)

                # update_package_schema_for_update interface
                package_schema = logic.schema.default_update_package_schema()
                for harvester in p.PluginImplementations(ISchemingDCATHarvester):
                    if hasattr(harvester, 'update_package_schema_for_update'):
                        package_schema = harvester.update_package_schema_for_update(package_schema)
                context['schema'] = package_schema

                package_dict['id'] = harvest_object.package_id
                try:
                    # before_update interface
                    for harvester in p.PluginImplementations(ISchemingDCATHarvester):
                        if hasattr(harvester, 'before_update'):
                            err = harvester.before_update(harvest_object, package_dict, harvester_tmp_dict)

                            if err:
                                self._save_object_error(f'TableHarvester plugin error: {err}', harvest_object, 'Import')
                                return False
                    
                    result = self._create_or_update_package(
                        package_dict, harvest_object, 
                        package_dict_form='package_show')

                    # after_update interface
                    for harvester in p.PluginImplementations(ISchemingDCATHarvester):
                        if hasattr(harvester, 'after_update'):
                            err = harvester.after_update(harvest_object, package_dict, harvester_tmp_dict)

                            if err:
                                self._save_object_error(f'TableHarvester plugin error: {err}', harvest_object, 'Import')
                                return False

                    log.info('Updated package %s with GUID: %s' % (package_dict["id"], harvest_object.guid))
                    
                except p.toolkit.ValidationError as e:
                    error_message = ', '.join(f'{k}: {v}' for k, v in e.error_dict.items())
                    self._save_object_error(f'Validation Error: {error_message}', harvest_object, 'Import')
                    return False

        return result

    def validate_config(self, config):
        """
        Validates the configuration for the harvester.

        Args:
            config (dict): The configuration dictionary.

        Returns:
            str: The validated configuration as a JSON string.

        Raises:
            ValueError: If the configuration is invalid.

        """
        config_obj = self.get_harvester_basic_info(config)
        auth = True

        supported_types = {st['name'] for st in self._database_types_supported.values() if st['active']}

        # Check basic validation config
        self._set_basic_validate_config(config)
        
        # Instance sql_field_mapping validator
        field_mapping_validator = FieldMappingValidator()

        if 'database_type' in config:
            database_type = config_obj['database_type']
            log.debug("database_type: %s ", database_type)
            if not isinstance(database_type, basestring):
                raise ValueError('database_type must be a string')

            if database_type not in supported_types:
                raise ValueError(f'database_type should be one of: {", ".join(supported_types)}')

            config = json.dumps({**config_obj, 'database_type': database_type})

        else:
            raise ValueError(f'database_type should be one of: {", ".join(supported_types)}')

        if 'credentials' in config:   
            required_keys = ['user', 'password', 'host', 'port', 'db']  
            credentials = config_obj['credentials']
            
            if not isinstance(credentials, dict):
                raise ValueError('credentials must be a dictionary')
            
            for key in required_keys:
                if key not in credentials:
                    raise ValueError(f'credentials needs key "{key}"')
            
            if not isinstance(credentials['port'], int):
                raise ValueError('"port" must be an integer')
        else:
            raise ValueError("credentials must exist and be a dictionary with the following structure: {'user': 'username', 'password': 'password', 'host': 'hostname', 'port': port_number, 'db': 'database'}")

        #TODO: Finalizar database_p_keys
        if 'database_p_keys' in config_obj:
            self._validate_dataset_pkeys(database_type, config_obj)

        # Check if 'field_mapping_schema_version' exists in the config
        if 'field_mapping_schema_version' not in config_obj:
            raise ValueError(f'Insert the schema version: "field_mapping_schema_version: <version>", one of {self._field_mapping_validator_versions} . More info: https://github.com/OpenDataGIS/ckanext-fototeca?tab=readme-ov-file#recolector-sql')
        else:
            # If it exists, check if it's an integer and in the allowed versions
            if not isinstance(config_obj['field_mapping_schema_version'], int) or config_obj['field_mapping_schema_version'] not in self._field_mapping_validator_versions:
                raise ValueError(f'field_mapping_schema_version must be an integer and one of {self._field_mapping_validator_versions}. Check the extension README for more info.')

        # Validate if exists a JSON contained the mapping field_names between the remote schema and the local schema        
        for mapping_name in ['dataset_field_mapping', 'distribution_field_mapping', 'resourcedictionary_field_mapping']:
            if mapping_name in config:
                field_mapping = config_obj[mapping_name]
                if not isinstance(field_mapping, dict):
                    raise ValueError(f'{mapping_name} must be a dictionary')

                schema_version = config_obj['field_mapping_schema_version']

                try:
                    # Validate field_mappings acordin schema versions
                    field_mapping = field_mapping_validator.validate(field_mapping, schema_version)
                except ValueError as e:
                    raise ValueError(f"The field mapping is invalid: {e}") from e

                config = json.dumps({**config_obj, mapping_name: field_mapping})

    #TODO: método para crear/actualizar los datasets e importado por otros harvesters
    def _create_or_update_package(
        self, package_dict, harvest_object, package_dict_form="rest"
    ):
        """
        Creates a new package or updates an existing one according to the
        package dictionary provided.

        The package dictionary can be in one of two forms:

        1. 'rest' - as seen on the RESTful API:

                http://datahub.io/api/rest/dataset/1996_population_census_data_canada

           This is the legacy form. It is the default to provide backward
           compatibility.

           * 'extras' is a dict e.g. {'theme': 'health', 'sub-theme': 'cancer'}
           * 'tags' is a list of strings e.g. ['large-river', 'flood']

        2. 'package_show' form, as provided by the Action API (CKAN v2.0+):

               http://datahub.io/api/action/package_show?id=1996_population_census_data_canada

           * 'extras' is a list of dicts
                e.g. [{'key': 'theme', 'value': 'health'},
                        {'key': 'sub-theme', 'value': 'cancer'}]
           * 'tags' is a list of dicts
                e.g. [{'name': 'large-river'}, {'name': 'flood'}]

        Note that the package_dict must contain an id, which will be used to
        check if the package needs to be created or updated (use the remote
        dataset id).

        If the remote server provides the modification date of the remote
        package, add it to package_dict['metadata_modified'].

        :returns: The same as what import_stage should return. i.e. True if the
                  create or update occurred ok, 'unchanged' if it didn't need
                  updating or False if there were errors.
        """
        assert package_dict_form in ("rest", "package_show")
        try:
            if package_dict is None:
                pass

            # Change default schema
            schema = default_create_package_schema()
            schema["id"] = [ignore_missing, unicode_safe]
            schema["__junk"] = [ignore]

            # Check API version
            if self.config:
                try:
                    api_version = int(self.config.get("api_version", 2))
                except ValueError:
                    raise ValueError("api_version must be an integer")
            else:
                api_version = 2

            user_name = self._get_user_name()
            context = {
                "model": model,
                "session": Session,
                "user": user_name,
                "api_version": api_version,
                "schema": schema,
                "ignore_auth": True,
            }

            if self.config and self.config.get("clean_tags", True):
                tags = package_dict.get("tags", [])
                package_dict["tags"] = self._clean_tags(tags)

            # Check if package exists. Can be overridden if necessary
            #existing_package_dict = self._check_existing_package_by_ids(package_dict)
            existing_package_dict = None

            # Flag this object as the current one
            harvest_object.current = True
            harvest_object.add()

            if existing_package_dict is not None:
                package_dict["id"] = existing_package_dict["id"]
                log.debug(
                    "existing_package_dict title: %s and ID: %s",
                    existing_package_dict["title"],
                    existing_package_dict["id"],
                )

                # In case name has been modified when first importing. See issue #101.
                package_dict["name"] = existing_package_dict["name"]

                # Check modified date
                if "metadata_modified" not in package_dict or package_dict[
                    "metadata_modified"
                ] > existing_package_dict.get("metadata_modified"):
                    log.info(
                        "Package ID: %s with GUID: %s exists and needs to be updated",
                        package_dict["id"],
                        harvest_object.guid,
                    )
                    # Update package
                    context.update({"id": package_dict["id"]})

                    # Map existing resource URLs to their resources
                    existing_resources = {
                        resource["url"]: resource["modified"]
                        for resource in existing_package_dict.get("resources", [])
                        if "modified" in resource
                    }

                    new_resources = existing_package_dict.get("resources", []).copy()
                    for resource in package_dict.get("resources", []):
                        # If the resource URL is in existing_resources and the resource's
                        # modification date is more recent, update the resource in new_resources
                        if (
                            "url" in resource
                            and resource["url"] in existing_resources
                            and "modified" in resource
                            and dateutil.parser.parse(resource["modified"]) > dateutil.parser.parse(existing_resources[resource["url"]])
                        ):
                            log.info('Resource dates - Harvest date: %s and Previous date: %s', resource["modified"], existing_resources[resource["url"]])

                            # Find the index of the existing resource in new_resources
                            index = next(i for i, r in enumerate(new_resources) if r["url"] == resource["url"])
                            # Replace the existing resource with the new resource
                            new_resources[index] = resource
                        # If the resource URL is not in existing_resources, add the resource to new_resources
                        elif "url" in resource and resource["url"] not in existing_resources:
                            new_resources.append(resource)
                            
                        if resource["url"] is None or resource["url"] == "" or "url" not in resource:
                            self._save_object_error(
                                "Warning: Resource URL is None. Add it!",
                                harvest_object,
                                "Import",
                            )

                    package_dict["resources"] = new_resources

                    for field in p.toolkit.aslist(
                        config.get("ckan.harvest.not_overwrite_fields")
                    ):
                        if field in existing_package_dict:
                            package_dict[field] = existing_package_dict[field]
                    try:
                        package_id = p.toolkit.get_action("package_update")(
                            context, package_dict
                        )
                        log.info(
                            "Updated package: %s with GUID: %s",
                            package_id,
                            harvest_object.guid,
                        )
                    except p.toolkit.ValidationError as e:
                        error_message = ", ".join(
                            f"{k}: {v}" for k, v in e.error_dict.items()
                        )
                        self._save_object_error(
                            f"Validation Error: {error_message}",
                            harvest_object,
                            "Import",
                        )
                        return False

                else:
                    log.info(
                        "No changes to package with GUID: %s, skipping..."
                        % harvest_object.guid
                    )
                    # NB harvest_object.current/package_id are not set
                    return "unchanged"

                # Flag this as the current harvest object
                harvest_object.package_id = package_dict["id"]
                harvest_object.save()

            else:
                # Package needs to be created
                package_dict["id"] = package_dict["identifier"]

                # Get rid of auth audit on the context otherwise we'll get an
                # exception
                context.pop("__auth_audit", None)

                # Set name for new package to prevent name conflict, see issue #117
                if package_dict.get("name", None):
                    package_dict["name"] = self._gen_new_name(package_dict["name"])
                else:
                    package_dict["name"] = self._gen_new_name(package_dict["title"])

                for resource in package_dict.get("resources", []):
                    if resource["url"] is None or resource["url"] == "" or "url" not in resource:
                        self._save_object_error(
                            "Warning: Resource URL is None. Add it!",
                            harvest_object,
                            "Import",
                        )

                log.info(
                    "Created new package ID: %s with GUID: %s",
                    package_dict["id"],
                    harvest_object.guid,
                )

                #log.debug('Package: %s', package_dict)
                harvest_object.package_id = package_dict["id"]
                # Defer constraints and flush so the dataset can be indexed with
                # the harvest object id (on the after_show hook from the harvester
                # plugin)
                harvest_object.add()

                model.Session.execute(
                    "SET CONSTRAINTS harvest_object_package_id_fkey DEFERRED"
                )
                model.Session.flush()

                try:
                    new_package = p.toolkit.get_action("package_create")(
                        context, package_dict
                    )
                    log.info(
                        "Created new package: %s with GUID: %s",
                        new_package["name"],
                        harvest_object.guid,
                    )
                except p.toolkit.ValidationError as e:
                    error_message = ", ".join(
                        f"{k}: {v}" for k, v in e.error_dict.items()
                    )
                    self._save_object_error(
                        f"Validation Error: {error_message}", harvest_object, "Import"
                    )
                    return False

            Session.commit()

            return True

        except p.toolkit.ValidationError as e:
            log.exception(e)
            self._save_object_error(
                "Invalid package with GUID: %s: %r"
                % (harvest_object.guid, e.error_dict),
                harvest_object,
                "Import",
            )
        except Exception as e:
            log.exception(e)
            self._save_object_error("%r" % e, harvest_object, "Import")

        return None


class ContentFetchError(Exception):
    pass

class ContentNotFoundError(ContentFetchError):
    pass

class RemoteResourceError(Exception):
    pass

class SearchError(Exception):
    pass

class ReadError(Exception):
    pass

class RemoteSchemaError(Exception):
    pass