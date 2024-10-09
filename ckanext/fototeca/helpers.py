import logging

import ckan.lib.helpers as h
import ckan.plugins as p

log = logging.getLogger(__name__)

all_helpers = {}

def helper(fn):
    """Collect helper functions into the ckanext.schemingdcat.all_helpers dictionary.

    Args:
        fn (function): The helper function to add to the dictionary.

    Returns:
        function: The helper function.
    """
    all_helpers[fn.__name__] = fn
    return fn

@helper
def fototeca_get_ign_base_url():
    """
    Retrieves the IGN base URL.

    Returns:
        str: The URL.
    """
    return p.toolkit.config.get('ckanext.fototeca.ign_base_url')

@helper
def fototeca_get_alternate_identifier_field():
    """
    Retrieves the alternate identifier field_name.

    Returns:
        str: The field_name of the ckanext-fototeca scheming schema.
    """
    return p.toolkit.config.get('ckanext.fototeca.postgres.alternate_identifier_field')