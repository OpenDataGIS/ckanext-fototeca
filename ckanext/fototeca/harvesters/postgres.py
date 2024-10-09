import logging
from ckanext.schemingdcat.harvesters.sql.postgres import SchemingDCATPostgresHarvester, PostgresDatabaseManager
from ckanext.fototeca.lib.fototeca import (
    normalize_temporal_dates,
    normalize_reference_system,
    normalize_resources,
    sql_clauses
)

log = logging.getLogger(__name__)

class FototecaPostgresHarvester(SchemingDCATPostgresHarvester):
    '''
    A custom harvester that overrides methods.
    '''

    def info(self):
        return {
            'name': 'fototeca_postgres_harvester',
            'title': 'Fototeca - PostgreSQL Database Harvester',
            'description': 'A PostgreSQL database harvester for CKAN'
        }
    
    db_manager = PostgresDatabaseManager()
    harvester_type = 'postgres'
    
    def _build_select_clause(self, schema, table, column, alias):
        """
        Builds a SELECT clause for a SQL query.

        Args:
            schema (str): The database schema name.
            table (str): The table name.
            column (str): The column name.
            alias (str): The alias to use for the selected column in the query results.

        Returns:
            str: A SELECT clause string.
        """
        return sql_clauses(schema, table, column, alias)
    
    def modify_package_dict(self, package_dict, harvest_object):
      '''
      Allows custom harvesters to modify the package dict before
      creating or updating the actual package.
      ''' 
      
      # Simplified check for 'temporal_start' and 'temporal_end'
      if all(key in package_dict for key in ['temporal_start', 'temporal_end']):
        package_dict = normalize_temporal_dates(package_dict)
      
      # Simplified check for 'reference_system'
      if package_dict.get('reference_system'):
        package_dict = normalize_reference_system(package_dict)
        
      # Check resources
      if package_dict.get("resources"):
        package_dict = normalize_resources(package_dict)
    
      return package_dict