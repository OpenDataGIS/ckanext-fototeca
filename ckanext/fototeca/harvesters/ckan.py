
import logging
from urllib.parse import urlparse
import re
import pandas as pd

from ckan.plugins.core import SingletonPlugin, implements

from ckanext.schemingdcat.harvesters.base import RemoteResourceError
from ckanext.schemingdcat.interfaces import ISchemingDCATHarvester
import ckanext.schemingdcat.helpers as sdct_helpers

from ckanext.fototeca.config import FOTOTECA_HARVESTER_MD_CONFIG, FOTOTECA_PUBLISHER_TYPES, FOTOTECA_CODELIST_MAPPING
from ckanext.fototeca.lib.fototeca import (
    normalize_temporal_dates,
    normalize_reference_system,
    normalize_resources,
    sql_clauses
)

log = logging.getLogger(__name__)


# TODO: Fototeca CKAN Harvester
class FototecaCKANHarvester(SingletonPlugin):
    '''
    A CKAN SchemingDCATHarvester extended for the Fototeca environment.
    '''

    implements(ISchemingDCATHarvester)

    def before_modify_package_dict(self, package_dict):
        log.debug('In FototecaCKANHarvester before_modify_package_dict')

        # Update URLs
        self._update_urls(package_dict)
                
        # Normalize Fototeca specific fields
        package_dict = self._normalize_fototeca_fields(package_dict)
        
        # Simplified check for 'temporal_start' and 'temporal_end'
        if all(key in package_dict for key in ['temporal_start', 'temporal_end']):
            package_dict = normalize_temporal_dates(package_dict)

        log.debug('AFTER package_dict: %s', package_dict)

        return package_dict, []
    
    @staticmethod
    def _update_urls(package_dict, url_fields=None):
        """
        Update URL fields in the package dictionary to ensure they start with 'http://' or 'https://'.

        If a URL field does not start with 'http://' or 'https://', 'https://' is prepended to it.

        Args:
            package_dict (dict): The package dictionary where URL fields are to be updated.
            url_fields (list, optional): A list of URL fields to be updated. Defaults to ['author_url', 'contact_url', 'publisher_url', 'maintainer_url'].

        Returns:
            dict: The updated package dictionary.
        """
        if url_fields is None:
            url_fields = ['author_url', 'contact_url', 'publisher_url', 'maintainer_url']

        for field in url_fields:
            url = package_dict.get(field)
            if url:
                parsed_url = urlparse(url)
                package_dict[field] = url if parsed_url.scheme else 'https://' + url

        return package_dict

    @staticmethod
    def _normalize_fototeca_fields(package_dict):
        """
        Normalize Fototeca specific fields in the package dictionary based on FOTOTECA_CODELIST_MAPPING.

        Args:
            package_dict (dict): The package dictionary where fields are to be normalized.

        Returns:
            dict: The updated package dictionary.
        """
        for field, mappings in FOTOTECA_CODELIST_MAPPING.items():
            if field in package_dict:
                value = package_dict[field]
                if isinstance(value, list):
                    package_dict[field] = [FototecaCKANHarvester._normalize_value(v, mappings) for v in value]
                else:
                    package_dict[field] = FototecaCKANHarvester._normalize_value(value, mappings)
        return package_dict

    @staticmethod
    def _normalize_value(value, mappings):
        """
        Normalize a single value based on the provided mappings.

        Args:
            value (str): The value to be normalized.
            mappings (list): The list of mappings to use for normalization.

        Returns:
            str: The normalized value.
        """
        for mapping in mappings:
            if value in mapping['accepted_values']:
                return mapping['value']
            if re.match(mapping['pattern'], value):
                return mapping['value']
        return value