
import logging

import ckanext.scheming.helpers as sh
import ckan.lib.helpers as h
from ckantoolkit import (
    config,
    get_validator,
    UnknownValidator,
    missing,
    Invalid,
    StopOnError,
    _,
    unicode_safe,
)

import ckanext.schemingdcat.helpers as sdct_helpers

log = logging.getLogger(__name__)

all_validators = {}


def validator(fn):
    """
    collect validator functions into ckanext.schemingdcat.all_validators dict
    """
    all_validators[fn.__name__] = fn
    return fn

def scheming_validator(fn):
    """
    Decorate a validator that needs to have the scheming fields
    passed with this function. When generating navl validator lists
    the function decorated will be called passing the field
    and complete schema to produce the actual validator for each field.
    """
    fn.is_a_scheming_validator = True
    return fn

@scheming_validator
@validator
def fototeca_spatial_validator(field, schema):
    """
    Returns a validator function that checks if the 'flight_spatial' value exists in pkg If it exists, it sets the value of the field to the value of the field ('spatial').

    Args:
        field (dict): Information about the field to be updated.
        schema (dict): The schema for the field to be updated.

    Returns:
        function: A validation function that can be used to update the field based on the presence of 'flight_spatial'.
    """
    def validator(key, data, errors, context):
        spatial = data.get(('flight_spatial', ))
        if spatial:
            data[key] = spatial

    return validator
