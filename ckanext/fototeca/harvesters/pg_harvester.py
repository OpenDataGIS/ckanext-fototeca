import logging
import json
from past.builtins import basestring
from ckanext.schemingdcat.harvesters.base import SchemingDCATHarvester, RemoteResourceError, ReadError, RemoteSchemaError
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

##gather_stage() y funciones llamadas desde el gather_stage()

    def gather_stage(self, harvest_job):
        
        source_url = harvest_job.source.url

        log.debug('In gater_stage with database: %s', source_url)
        
        content_dict = {}
        self._names_taken = []
        
        # obtener Opciones de configuración
        if harvest_job.source.config:
            self._set_config(harvest_job.source.config)
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

        ##TODO Query de prueba para probar si todas las tablas existen y la conexión es correcta 
        log.debug(database_mapping)
        with engine.connect() as conn:
            query = self._create_query(database_mapping['fields'],database_mapping['p_key'])
            log.debug(query)
            result = conn.execute(text(query))
            dataList = result.fetchall()
    
        self.data = pd.DataFrame(data=dataList, columns=list(database_mapping["fields"].keys()))
        log.debug(self.data)
        return []

    def _create_query(self,fields,p_key):
        fieldsJoined = " ,".join(list(fields.values()))
        log.debug(fieldsJoined)
        p_keyList = list(p_key.items())
        query = "select "+fieldsJoined

        if 'oneTable' not in p_key:
            table1 = ".".join(p_keyList[0][0].split('.')[0:2])
            table2 = ".".join(p_keyList[0][1].split('.')[0:2])
            query += " from "+ table1+ " join "+table2 +" on "+ p_keyList[0][0] +"="+ p_keyList[0][1]

            for field in p_keyList[1:]:
                table1 = ".".join(field.split[0]('.')[0:2])
                table2 = ".".join(field.split[1]('.')[0:2])
                query += " from "+ table1+ " join "+table2 +" on "+ field[0] +"="+ field[1]
        else:
            table2 = ".".join(p_keyList[0][1].split('.')[0:2])
            query += " from " + table2
        
        return query

##fetch stage y funciones del fetch stage
    ##TODO implementar el fetch_stage
    #esta parte necesita tomar el engine creado en gather_stage, generar una sentencia SQL que se base en las keys del config, realizar la petición SQL y guardar los datos en un dataframe de pandas que se usará en el import_stage()
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