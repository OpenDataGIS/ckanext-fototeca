import logging

import ckan.lib.helpers as h
import ckan.plugins as p

import ckanext.fototeca.config as f_config


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
    return f_config.ign_base_url