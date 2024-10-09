import logging

import ckan.plugins as p

from ckanext.schemingdcat.harvesters.sql.postgres import SchemingDCATPostgresHarvester, PostgresDatabaseManager

from ckanext.fototeca.lib.fototeca import (
    normalize_temporal_dates,
    normalize_reference_system,
    normalize_resources,
    sql_clauses,
    normalize_fototeca_fields
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

      # Normalize Fototeca specific fields
      package_dict = normalize_fototeca_fields(package_dict)

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
    
    def _process_content(self, content_dicts, conn_url, field_mapping):
        """
        Processes the SQL query content_dicts based on the field_mapping, handling multilingual fields by appending -lang to the original field name for each available language.
        """

        log.debug('In FototecaPostgresHarvester process_content: %s', self.obfuscate_credentials_in_url(conn_url))
        
        fototeca_alternate_identifier_field = p.toolkit.config.get('ckanext.fototeca.postgres.alternate_identifier_field')
        
        # Clean datasets
        table_datasets = self._clean_table_datasets(content_dicts['datasets'])
        
        # Clean distributions
        dataset_id_colname = self._field_mapping_info['distribution_field_mapping'].get('parent_resource_id')
        if content_dicts.get('distributions') is not None and not content_dicts['distributions'].empty:
            table_distributions_grouped = self._clean_table_distributions(content_dicts['distributions'], dataset_id_colname)
        else:
            log.debug('No distributions loaded. Check "distribution.%s" fields', dataset_id_colname)
            table_distributions_grouped = None
        
        # Clean datadictionaries
        distribution_id_colname = self._field_mapping_info['datadictionary_field_mapping'].get('parent_resource_id')
        if content_dicts.get('datadictionaries') is not None and not content_dicts['datadictionaries'].empty:
            table_datadictionaries_grouped = self._clean_table_datadictionaries(content_dicts['datadictionaries'], distribution_id_colname)
        else:
            table_datadictionaries_grouped = None

        return self._add_distributions_and_datadictionaries_to_datasets(table_datasets, table_distributions_grouped, table_datadictionaries_grouped, identifier_field='identifier', alternate_identifier_field=fototeca_alternate_identifier_field)