
import logging
from datetime import datetime

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

@scheming_validator
@validator
def fototeca_year_validator(field, schema):
    """
    Returns a validator function that extracts the year from an ISO date in the 'temporal_start' field and sets it to the field.

    Args:
        field (dict): Information about the field to be updated.
        schema (dict): The schema for the field to be updated.

    Returns:
        function: A validation function that extracts the year from 'temporal_start' and sets it to the field.
    """
    def validator(key, data, errors, context):
        temporal_start = data.get(('temporal_start', ))
        if temporal_start:
            try:
                # Parse the ISO date and extract the year
                flight_year = datetime.fromisoformat(temporal_start).year
                data[key] = flight_year
            except ValueError:
                errors[key].append('Invalid date format for temporal_start')

    return validator

@scheming_validator
@validator
def fototeca_flight_coating_validator(field, schema):
    """
    Returns a validator function that checks if the 'flight_longitudinal' and 'flight_transverse' fields are present only for specific flights.

    Args:
        field (dict): Information about the field to be updated.
        schema (dict): The schema for the field to be updated.

    Returns:
        function: A validation function that checks the presence of 'flight_longitudinal' and 'flight_transverse' based on 'flight_type'.
    """
    def validator(key, data, errors, context):
        flight_type = data.get(('flight_type', ))
        log.debug('flight_type: %s', key)
        flight_longitudinal = data.get(('flight_longitudinal', ))
        flight_transverse = data.get(('flight_transverse', ))

        if flight_type == 'analogico':
            if flight_transverse is not None and flight_transverse != '' and flight_transverse != 0:
                errors[('flight_transverse', )].append('There must be no transverse coating on analogical flights.')
        elif flight_type == 'digital':
            if flight_longitudinal is not None and flight_longitudinal != '' and flight_transverse != 0:
                errors[('flight_longitudinal', )].append('There must be no longitudinal overlap on digital flights.')

    return validator

@scheming_validator
@validator
def fototeca_valid_percentage(field, schema):
    """
    Validator that checks if a value is a natural number between 0 and 100.
    """
    def validator(key, data, errors, context):
        value = data.get(key)
        log.debug('percentage value: %s', value)
        if value is None or value == '':
            return  # Skip validation if value is None or an empty string
        try:
            value = int(value)
            log.debug('percentage int value: %s', value)
            if not (0 <= value <= 100):
                errors[key].append('Must be a natural number between 0 and 100.')
        except (ValueError, TypeError):
            errors[key].append('Must be a natural number between 0 and 100.')
    return validator
