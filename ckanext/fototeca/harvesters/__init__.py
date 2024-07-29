from ckanext.fototeca.harvesters.base import SQLHarvester
from ckanext.fototeca.harvesters.postgres import PostgresHarvester
from ckanext.fototeca.harvesters.ckan import FototecaCKANHarvester

__all__ = ['SQLHarvester', 'PostgresHarvester', 'FototecaCKANHarvester']