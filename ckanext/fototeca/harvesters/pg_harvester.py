from ckanext.schemingdcat.harvesters.base import SchemingDCATHarvester, RemoteResourceError, ReadError, RemoteSchemaError


class FototecaPGHarvester(SchemingDCATHarvester):
    def info(self):
        return {
            'name': 'fototeca_pg_harvester',
            'title': 'Recolector de base de datos SQL',
            'description': 'Un recolector de base de datos SQL para CKAN'
        }

    def gather_stage(self, harvest_job):
        # Aquí iría el código para recopilar los identificadores de los objetos a recolectar de la API REST.
        return []

    def fetch_stage(self, harvest_object):
        # Aquí iría el código para extraer los datos del objeto de la API REST.
        return True

    def import_stage(self, harvest_object):
        # Aquí iría el código para crear o actualizar el conjunto de datos en CKAN.
        return True