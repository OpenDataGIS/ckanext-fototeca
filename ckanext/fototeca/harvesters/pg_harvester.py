import logging
import json
from past.builtins import basestring
from ckanext.schemingdcat.harvesters.base import SchemingDCATHarvester, RemoteResourceError, ReadError, RemoteSchemaError


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

    def gather_stage(self, harvest_job):
        # Aquí iría el código para recopilar los identificadores de los objetos a recolectar de la API REST.
        source_url = harvest_job.source.credentials.url
        
        log.debug('In gater_stage with database: %s', source_url)
        
        content_dict = {}
        self._names_taken = []
        
        # Get config options
        if harvest_job.source.config:
            self._set_config(harvest_job.source.config)

        return []

    def fetch_stage(self, harvest_object):
        # Aquí iría el código para extraer los datos del objeto de la API REST.
        return True

    def import_stage(self, harvest_object):
        # Aquí iría el código para crear o actualizar el conjunto de datos en CKAN.
        return True

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
                                    passdataset_sheet
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