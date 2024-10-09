
import logging
from urllib.parse import urlparse

from ckan.plugins.core import SingletonPlugin, implements

from ckanext.schemingdcat.interfaces import ISchemingDCATHarvester

from ckanext.fototeca.lib.fototeca import (
    normalize_temporal_dates,
    normalize_reference_system,
    normalize_resources,
    normalize_fototeca_fields
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
        package_dict = normalize_fototeca_fields(package_dict)
        
        # Simplified check for 'temporal_start' and 'temporal_end'
        if all(key in package_dict for key in ['temporal_start', 'temporal_end']):
            package_dict = normalize_temporal_dates(package_dict)

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
