
import logging
from urllib.parse import urlparse
import mimetypes
import requests
import re
import pandas as pd

from ckan.plugins.core import SingletonPlugin, implements

from ckanext.schemingdcat.harvesters.base import RemoteResourceError
import ckanext.schemingdcat.helpers as sdct_helpers

import ckanext.fototeca.helpers as f_helpers
from ckanext.fototeca.config import FOTOTECA_HARVESTER_MD_CONFIG, FOTOTECA_PUBLISHER_TYPES
from ckanext.fototeca.interfaces import ISQLHarvester

from ckanext.schemingdcat.config import (
    COMMON_DATE_FORMATS,
    mimetype_base_uri,
    URL_FIELD_NAMES,
    EMAIL_FIELD_NAMES,
    OGC2CKAN_MD_FORMATS,
)

log = logging.getLogger(__name__)


# TODO: PostgreSQL Harvester
class PostgresHarvester(SingletonPlugin):
    '''
    An enhanced bulk metadata upload harvester for IEPNB.
    '''
    _field_choices = None
    _default_lang = 'es'

    implements(ISQLHarvester)