import logging
import json
import hashlib
from past.builtins import basestring
from ckanext.harvest.harvesters.base import HarvesterBase
from ckanext.harvest.model import HarvestObject, HarvestObjectExtra
from ckanext.schemingdcat.harvesters.base import SchemingDCATHarvester, RemoteResourceError, ReadError, RemoteSchemaError
from ckanext.schemingdcat.interfaces import ISchemingDCATHarvester
from ckanext.schemingdcat.lib.field_mapping import FieldMappingValidator
from ckanext.fototeca.lib.routingSQL.sql_routing_pg import routingPG

import pandas as pd 

from ckan import logic
from ckan.logic import NotFound, get_action
import ckan.plugins as p
import ckan.model as model

log = logging.getLogger(__name__)


class FototecaSQLHarvester(SchemingDCATHarvester):
    def info(self):
        return {
            'name': 'fototeca_pg_harvester',
            'title': 'Recolector de base de datos SQL',
            'description': 'Un recolector de base de datos SQL para CKAN'
        }

    _storage_types_supported = [
        {
            'name':'postgres',
            'title':'Postgre SQL',
            'active':True
        }
    ]

    _database_type = "postgres"
    _credentials = None
    data = None
    config = None

##gather_stage() y funciones llamadas desde el gather_stage()

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

        ###definición de engines de SQLrouting
        ##En caso de querer agregar nuevas bases de datos añadirlas con 
        ##elif al condicional
        if database_type == "postgres":
            log.debug("starting database remote schema harvest")
            database = routingPG(credentials['user'],credentials['password'],credentials['host'],credentials['port'],credentials['db'])
        else:
            raise ValueError("unsupported database reached gather stage")

        keys = []
        values = []

        log.debug(dataset_field_mapping)

        for key, value in dataset_field_mapping.items():
            keys.append(str(key))
            values.append(str(value["field_namegit"]))

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

        # Comprobar guids para crear, borrar o cambiar
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
    

##fetch stage y funciones del fetch stage

    def fetch_stage(self, harvest_object):
    #vacío porque los datos ya estan recopilados en gather_stage
        return True

##import stage y funciones del import stage
    ##TODO implementar el import stage 
    #esta parte debe recopilar el dataframe de pandas 
    def import_stage(self, harvest_object):
        # Aquí iría el código para crear o actualizar el conjunto de datos en CKAN.
        log.debug("In FototecaPGHarvester import stage")

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

        return True



##validate config y funciones del validate config
    def validate_config(self,config):
        supported_types = ', '.join([st['name'] for st in self._storage_types_supported if st['active']])
        config_obj = self.get_harvester_basic_info(config)
        #log.debug(self._is_not_db_key("1.2.3"))

        
        if 'database_type' in config:
            database_type = config_obj['database_type']
            log.debug("database_type = "+ database_type)
            if not isinstance(database_type, basestring):
                raise ValueError('database_type must be a string')

            if database_type not in supported_types:
                raise ValueError(f'database_type should be one of: {supported_types}')

            config = json.dumps({**config_obj, 'database_type': database_type})

        else:
            raise ValueError(f'database_type should be one of: {supported_types}')

        if 'credentials' in config:
            credentials = config_obj['credentials']
            if not isinstance(credentials, dict):
                raise ValueError('credentials must be a dictionary')
            else:
                if 'user' in credentials:
                    if 'password' in credentials:
                        if 'host' in credentials:
                            if 'port' in credentials:
                                if 'db' in credentials:
                                    pass
                                else:
                                    raise ValueError('credentials needs key "db"')
                                if not isinstance(credentials['port'],int):
                                    raise ValueError('port must be an integer')
                            else:
                                raise ValueError('credentials needs key "port"')
                        else:
                            raise ValueError('credentials needs key "host"')
                    else:
                        raise ValueError('credentials needs key "password"')
                else:
                    raise ValueError('credentials needs key "user"')
        else:
            raise ValueError('credentials must exist')

        # Check if 'field_mapping_schema_version' exists in the config
        if 'field_mapping_schema_version' not in config_obj:
            raise ValueError(f'Insert the schema version: "field_mapping_schema_version: <version>", one of {self._field_mapping_validator_versions} . More info: https://github.com/mjanez/ckanext-schemingdcat?tab=readme-ov-file#remote-google-sheetonedrive-excel-metadata-upload-harvester')
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

                if schema_version == 1:
                    # Check if the config is a valid mapping for schema version 1
                    for local_field, remote_field in field_mapping.items():
                        if not isinstance(local_field, str):
                            raise ValueError('"local_field_name" must be a string')
                        if not isinstance(remote_field, (str, dict)):
                            raise ValueError('"remote_field_name" must be a string or a dictionary')
                        if isinstance(remote_field, dict):
                            for lang, remote_field_name in remote_field.items():
                                if not isinstance(lang, str) or not isinstance(remote_field_name, str):
                                    raise ValueError('In translated fields, both language and remote_field_name must be strings. eg. "notes_translated": {"es": "notes-es"}')
                                if not re.match("^[a-z]{2}$", lang):
                                    raise ValueError('Language code must be a 2-letter ISO 639-1 code')
                else:
                    # Check if the config is a valid mapping for schema version 2
                    for local_field, field_config in field_mapping.items():
                        if not isinstance(local_field, str):
                            raise ValueError('"local_field_name" must be a string')
                        if not isinstance(field_config, dict):
                            raise ValueError('"field_config" must be a dictionary')

                        # Check field properties
                        for prop, value in field_config.items():
                            if prop not in ['field_value', 'field_position', 'field_name', 'languages', "sort", "es", "en"]:
                                raise ValueError(f'Invalid property "{prop}" in field_config. Check: https://github.com/mjanez/ckanext-schemingdcat?tab=field-mapping-structure')
                            if prop in ['field_value', 'field_position', 'field_name'] and not isinstance(value, (str, list)):
                                raise ValueError(f'"{prop}" must be a string: "value_1" or a list: "["value_1", "value_2"]')

                            #TODO: _is_not_db_key
                            if prop in ['field_name']:
                                # if value _is_not_db_key
                                    value_split = value.split('.')
                                    if len(value_split) != 3:
                                        raise ValueError(f'"The lenght of the field: {local_field} is: {len(value)} on {value}"')

                            if prop == 'languages':
                                if not isinstance(value, dict):
                                    raise ValueError('"languages" must be a dictionary')
                                for lang, lang_config in value.items():
                                    if not isinstance(lang, str) or not re.match("^[a-z]{2}$", lang):
                                        raise ValueError('Language code must be a 2-letter ISO 639-1 code')
                                    if not isinstance(lang_config, dict):
                                        raise ValueError('Language config must be a dictionary')
                                    for lang_prop, lang_value in lang_config.items():
                                        if lang_prop not in ['field_value', 'field_position', 'field_name']:
                                            raise ValueError(f'Invalid property "{lang_prop}" in language config')
                                        if not isinstance(lang_value, (str, list)):
                                            raise ValueError(f'"{lang_prop}" must be a string or a list')

                config = json.dumps({**config_obj, mapping_name: field_mapping})

        if 'database_p_keys' in config:
            database_p_keys = config_obj['database_p_keys']
            log.debug("database_type = "+ database_p_keys)
            if not isinstance(database_p_keys, basestring):
                raise ValueError('database_type must be a string')

            #TODO: Loop over database_p_keys


            config = json.dumps({**config_obj, 'database_type': database_type})



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

