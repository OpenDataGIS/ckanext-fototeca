import logging

import re

import ckan.plugins as p

import ckanext.schemingdcat.helpers as sdct_helpers

from ckanext.fototeca.config import FOTOTECA_CODELIST_MAPPING

log = logging.getLogger(__name__)

epsg_uri_template = "http://www.opengis.net/def/crs/EPSG/0/{srid}"

def normalize_fototeca_fields(package_dict):
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
                package_dict[field] = [normalize_value(v, mappings) for v in value]
            else:
                package_dict[field] = normalize_value(value, mappings)
    return package_dict

def normalize_value(value, mappings):
    """
    Normalize a single value based on the provided mappings.

    Args:
        value (str): The value to be normalized.
        mappings (list): The list of mappings to use for normalization.

    Returns:
        str: The normalized value.
    """
    value = value.lower()

    for mapping in mappings:
        if value in [v.lower() for v in mapping['accepted_values']]:
            return mapping['value']
        if re.match(mapping['pattern'], value, re.IGNORECASE):
            return mapping['value']
    return value

# Aux defs for Fototeca import_stage validation
def normalize_temporal_dates(package_dict):
  """
  Normalizes 'temporal_start' and 'temporal_end' in a dictionary to YYYY-MM-DD format.

  Modifies 'temporal_start' and 'temporal_end' in `package_dict` to represent the first and last day of the year(s) specified. 
  Input can be a comma-separated string or a list of years.

  Args:
    package_dict (dict): Dictionary with 'temporal_start' and/or 'temporal_end' keys.

  Returns:
    None: Modifies `package_dict` in-place.
  """
  # Convert to standard date string assuming the first or last day of the selected year
  for key in ['temporal_start', 'temporal_end']:
    if key in package_dict:
      # Convert the value to a list of years if it's a string
      years = [int(year) for year in package_dict[key].split(',')] if isinstance(package_dict[key], str) else package_dict[key]
      
      # Select the appropriate year
      selected_year = min(years) if key == 'temporal_start' else max(years)
      
      # Convert to standard date string
      date_str = f"{selected_year}-01-01" if key == 'temporal_start' else f"{selected_year}-12-31"
      package_dict[key] = date_str
      
  return package_dict
      
def normalize_reference_system(package_dict):
  """
  Simplifies the normalization process by taking the SRID value as text and keeping everything to the left of the decimal point.

  Args:
    value (str): The SRID value as a string, which may contain decimals.

  Returns:
    str: The EPSG URI corresponding to the simplified SRID value.
  """ 
  try: 
    package_dict['reference_system'] = epsg_uri_template.format(srid=package_dict['reference_system'].split('.')[0] )
    return package_dict
    
  except Exception as e:
    raise ValueError('SRID value is not a valid number: %s', package_dict['reference_system']) from e


def normalize_resources(package_dict):
    """Filters out resources without a non-empty URL from the package dictionary.

    This function iterates over the resources in the given package dictionary. It keeps only those resources that have a non-empty URL field. The filtered list of resources is then reassigned back to the package dictionary.

    Args:
        package_dict (dict): A dictionary representing the package, which contains a list of resources.

    """
    # Filter resources that have a non-empty URL
    filtered_resources = [resource for resource in package_dict.get("resources", []) if resource.get('url')]
    
    # Reassign the filtered list of resources back to the package_dict
    package_dict["resources"] = filtered_resources
    
    return package_dict
# Specific SQL clauses
def sql_clauses(schema, table, column, alias):
  """
  Generates a SQL expression for GeoJSON data, spatial reference system, or other data with conditional logic based on length or alias.

  This function constructs a SQL expression to select data from a specified column. For GeoJSON data, if the data length exceeds a predefined limit set in `ckanext.fototeca.postgres.geojson_chars_limit`, the expression returns NULL to avoid performance issues with large GeoJSON objects. Otherwise, it returns the GeoJSON data. For geographic columns, it applies a transformation to the EPSG:4326 coordinate system and simplifies the geometry based on a tolerance value defined in `postgres.geojson_tolerance`. If the alias is 'reference_system', it returns the SRID of the geometry.

  Parameters:
  - schema (str): The database schema name.
  - table (str): The table name where the column is located.
  - column (str): The column name containing GeoJSON data or geometry.
  - alias (str): The alias to use for the resulting column in the SQL query.

  Returns:
  - str: A SQL expression as a string.
  """
  postgres_geojson_chars_limit = p.toolkit.config.get('ckanext.schemingdcat.postgres.geojson_chars_limit')
  postgres_geojson_tolerance = p.toolkit.config.get('ckanext.schemingdcat.postgres.geojson_tolerance')
  
  if alias == 'spatial':
    # NULL if SRID=0
    return f"CASE WHEN ST_SRID({schema}.{table}.{column}) = 0 THEN NULL ELSE ST_AsGeoJSON(ST_Transform(ST_Envelope({schema}.{table}.{column}), 4326), 2) END AS {alias}"

  elif alias == 'flight_spatial':
    # NULL if SRID=0
    return f"CASE WHEN ST_SRID({schema}.{table}.{column}) = 0 THEN NULL ELSE CASE WHEN LENGTH(ST_AsGeoJSON(ST_Simplify(ST_Transform({schema}.{table}.{column}, 4326), {postgres_geojson_tolerance}), 2)) <= {postgres_geojson_chars_limit} THEN ST_AsGeoJSON(ST_Simplify(ST_Transform({schema}.{table}.{column}, 4326), {postgres_geojson_tolerance}), 2) ELSE NULL END END AS {alias}"

  elif alias == 'reference_system':
    return f"ST_SRID({schema}.{table}.{column}) AS {alias}"

  else:
    return f"{schema}.{table}.{column} AS {alias}"