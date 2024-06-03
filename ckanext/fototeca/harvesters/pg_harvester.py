import logging
import json
import hashlib
from past.builtins import basestring
from ckanext.harvest.harvesters.base import HarvesterBase
from ckanext.harvest.model import HarvestObject, HarvestObjectExtra
from ckanext.schemingdcat.harvesters.base import SchemingDCATHarvester, RemoteResourceError, ReadError, RemoteSchemaError
from ckanext.schemingdcat.interfaces import ISchemingDCATHarvester
import psycopg2
import pandas as pd 
from sqlalchemy import engine, create_engine, text


from ckan import logic
from ckan.logic import NotFound, get_action
import ckan.plugins as p
import ckan.model as model

log = logging.getLogger(__name__)


class FototecaPGHarvester(SchemingDCATHarvester):
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
            database_mapping = self.config.get("database_mapping")

        ##definición de engines de SQLalchemy
        #En caso de querer agregar nuevas bases de datos añadirlas con 
        #elif al condicional
        if database_type == "postgres":
            engine_params = "postgresql+psycopg2://"+credentials["user"]+":"+credentials["password"]+"@"+credentials["host"]+":"+str(credentials["port"])+"/"+credentials["db"]
            log.debug(engine_params)
            engine = create_engine(engine_params)
        else:
            raise ValueError("unsupported database reached gather stage")

        ##realizar query y obtener los valores de la base de datos
        log.debug(database_mapping)
        with engine.connect() as conn:
            query = self._create_query(database_mapping['fields'],database_mapping['p_key'])
            log.debug(query)
            result = conn.execute(text(query))
            dataList = result.fetchall()
    
        self.data = pd.DataFrame(data=dataList, columns=list(database_mapping["fields"].keys()))
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
        

        ##TODO implementar condicionales de new/delete/change 
        new = guids_in_harvest 

        ##Generamos HarvestObject
        ids = []
        for guid in new:
            log.debug("guid: "+ guid)
            log.debug(datasets_to_harvest.get(guid).to_dict())
            obj = HarvestObject(guid=guid, job=harvest_job, content=json.dumps(datasets_to_harvest.get(guid).to_dict()),
                                extras=[HarvestObjectExtra(key='status', value='new')])
        #    obj.save()
        #    ids.append(obj.id)

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
        return True


##validate config y funciones del validate config
    def validate_config(self,config):
        supported_types = ', '.join([st['name'] for st in self._storage_types_supported if st['active']])
        config_obj = self.get_harvester_basic_info(config)
        log.debug(self._isNotDBKey("1.2.3"))

        
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

        if 'database_mapping' in config:
            database_mapping = config_obj['database_mapping']

            if not isinstance(next(iter(database_mapping)),dict):
                ValueError('database_mapping must be a collection of dictionaries')
            else:
                if 'p_key' in database_mapping:
                    if not isinstance(database_mapping['p_key'],dict):
                        ValueError('p_key must be a dictionary')
                    else:
                        if self._isNotDBKey(next(iter(database_mapping['p_key']))):
                            ValueError('wrong "p_key" database field format; should be schema.table.value')
                        
                    if not isinstance(database_mapping['fields']):
                        ValueError('fields must be a dictionary')
                    else:
                        if self._isNotDBKey(next(iter(database_mapping['fields']))):
                            ValueError('wrong "fields" database field format; should be schema.table.value')


    def _isNotDBKey(self, string):
        field = string.split('.')
        return field != 3

