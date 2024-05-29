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
    _engine = None
    

##gather_stage() y funciones llamadas desde el gather_stage()
    def gather_stage(self, harvest_job):
        
        source_url = harvest_job.source.url

        log.debug('In gater_stage with database: %s', source_url)
        
        content_dict = {}
        self._names_taken = []
        
        # Get config options
        if harvest_job.source.config:
            self._set_config(harvest_job.source.config)
            database_type = self.config.get("database_type")
            credentials = self.config.get("credentials")
            database_mapping = self.config.get("database_mapping")

        if database_type == "postgres":
            engine_params = "postgresql+psycopg2://"+credentials["user"]+":"+credentials["password"]+"@"+credentials["host"]+":"+str(credentials["port"])+"/"+credentials["db"]
            log.debug(engine_params)
            self.engine = create_engine(engine_params)
        else:
            raise ValueError("unsupported database reached gather stage")

        ##TODO Query de prueba para probar si todas las tablas existen y la conexión es correcta 
        with self.engine.connect() as conn:
            result = conn.execute(text("select * from ways limit 20"))
            log.debug(result.first())

        
        return []
    
##fetch stage y funciones del fetch stage
    ##TODO implementar el fetch_stage
    #esta parte necesita tomar el engine creado en gather_stage, generar una sentencia SQL que se base en las keys del config, realizar la petición SQL y guardar los datos en un dataframe de pandas que se usará en el import_stage()
    def fetch_stage(self, harvest_object):
        # Aquí iría el código para extraer los datos del objeto de la API REST.
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
                        if _isNotDBKey(next(iter(database_mapping['p_key']))):
                            ValueError('wrong "p_key" database field format; should be schema.table.value')
                    if not isinstance(database_mapping['fields']):
                        ValueError('fields must be a dictionary')
                    else:
                        if _isNotDBKey(next(iter(database_mapping['fields']))):
                            ValueError('wrong "fields" database field format; should be schema.table.value')


    def _isNotDBKey(string):
        field = string.split('.')
        return field != 3