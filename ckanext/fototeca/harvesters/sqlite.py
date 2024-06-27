import logging
import sqlite3
from urllib.parse import urlparse

from ckan.plugins.core import SingletonPlugin, implements

from ckanext.schemingdcat.harvesters.base import RemoteResourceError
import ckanext.schemingdcat.helpers as sdct_helpers

import ckanext.fototeca.helpers as f_helpers
from ckanext.fototeca.harvesters.base import SQLHarvester, DatabaseManager
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


class SqliteDatabaseManager(DatabaseManager):
    def connect(self):
        self._connection = sqlite3.connect(self.db_path)

    def disconnect(self):
        if self._connection:
            self._connection.close()

    def execute_query(self, query):
        pass

# TODO: SQLite Harvester using interfaces
class SqliteHarvester(SQLHarvester):
    """
    A custom harvester for harvesting SQLite databases using the Fototeca extension.

    It extends the base `SQLHarvester` class.
    """

    def info(self):
        return {
            'name': 'fototeca_sqlite_harvester',
            'title': 'SQLite Database Harvester',
            'description': 'An SQLite database harvester for CKAN'
        }
    
    db_manager = SqliteDatabaseManager()
    _db_path = None
    _connection = None