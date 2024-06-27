from ckan.plugins.interfaces import Interface


class ISQLHarvester(Interface):
    """
    This is a harvesting interface for SQL databases that provides a set of methods to be implemented by a harvester. 
    The methods are designed to be called at different stages of the harvesting process, allowing for 
    customization and extension of the default behavior. 

    The methods include hooks before the retrieval of the SQL data and when an error occurs during the retrieval. 

    Each method is documented with its purpose, parameters, and return values.
    """

    def before_sql_retrieve(self, field_mappings, conn_url, harvest_job):
        """
        Performs operations on field mappings before the SQL data retrieval.

        This method allows for preprocessing or modification of the field mappings
        based on the harvest job or other criteria before they are used to construct
        the SQL query for data retrieval.

        Args:
            field_mappings (dict): A dictionary defining how database fields map to the desired structure.
            conn_url (str): The connection URL for the remote database.
            harvest_job (object): A ``HarvestJob`` domain object which contains a
                                  reference to the harvest source (``harvest_job.source``).

        Returns:
            tuple: A tuple with two items:
                    * Modified field mappings. If this is False, the gather stage will stop.
                    * A list of error messages. These will get stored as gather
                      errors by the harvester.
        """
        return field_mappings, []
    
    def after_sql_retrieve(self, content_dicts, harvest_job):
        """
        Called just after the SQL data is retrieved

        Args:
            content_dicts (dict): A dict of dataframes containing the content of the harvested database(datasets, distributions and datadictionaries).
            harvest_job (object): A ``HarvestJob`` domain object which contains a
                                  reference to the harvest source (``harvest_job.source``).

        Returns:
            tuple: A tuple with two items:
                    * The file content_dicts. If this is False the gather stage will
                      stop.
                    * A list of error messages. These will get stored as gather
                      errors by the harvester
        """
        return content_dicts, []

    def before_cleaning(self, content_dicts):
        """
        This method is called before the cleaning process starts.

        Args:
            content_dicts (dict): A dict of dataframes containing the content of the harvested dataset (datasets, distributions and datadictionaries).

        Returns:
            tuple: A tuple with two items:
                    * The remote sheet content_dicts with all datasets, distributions and datadictionaries dicts.
                    * A list of error messages. These will get stored as gather errors by the harvester.
        """
        return content_dicts, []

    def after_cleaning(self, clean_datasets):
        """
        This method is called after the cleaning process ends.

        Args:
            clean_datasets (list): The cleaned datasets.

        Returns:
            tuple: A tuple with two items:
                    * The cleaned datasets list of dictionaries.
                    * A list of error messages. These will get stored as gather errors by the harvester.
        """
        return clean_datasets, []

    def handle_sql_retrieve_errors(self, exception, harvest_job):
        """
        Called when an error occurs while retrieving data from the SQL database

        Args:
            exception (Exception): The exception that was raised during data retrieval
            harvest_job (object): A ``HarvestJob`` domain object which contains a
                                  reference to the harvest source (``harvest_job.source``).

        Returns:
            list: A list of error messages. These will get stored as gather
                  errors by the harvester
        """
        return [str(exception)]