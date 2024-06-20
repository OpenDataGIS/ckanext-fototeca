import re
import logging

log = logging.getLogger(__name__)

from ckanext.schemingdcat.lib.field_mapping import FieldMappingValidator


class SqlFieldMappingValidator(FieldMappingValidator):
    def __init__(self):
        super().__init__()

        # Override valid_props and validators
        self.valid_props = {'field_value', 'field_name', 'sort', 'languages'}
        self.validators = {
            1: self.validate_v1
        }        

    def _is_not_integer(self, local_field, prop, value):
        """
        Checks if the given value is not an integer.

        This function checks if the given value is not an integer.
        It raises a ValueError if the value is not an integer.

        Args:
            local_field (str): The local field to check.
            prop (str): The property to check. This function only checks the property 'sort'.
            value (str): The value to check.

        Raises:
            ValueError: If the value is not an integer.
        """
        if prop == 'sort':
            if not isinstance(value, int):
                raise ValueError('The property "%s" in field: "%s" should be an integer. It currently is: "%s"' % (prop, local_field, type(value).__name__))

    def _is_not_db_key(self, local_field, prop, value):
        """
        Checks if the given value is not a database key.

        This function checks if the given value is not in the format of a database key, i.e., '{schema}.{table}.{field}'.
        It raises a ValueError if the value is not in the correct format.

        Args:
            local_field (str): The local field to check.
            prop (str): The property to check. This function only checks the property 'field_name'.
            value (str): The value to check.

        Raises:
            ValueError: If the value is not in the format of a database key.
        """
        if prop == 'field_name':
            value_split = value.split('.')
            if len(value_split) != 3:
                raise ValueError('The field: "%s" should be in the format: {schema}.{table}.{field}. It currently has "%d" parts: "%s"' % (local_field, len(value_split), value))

    def validate_v1(self, field_mapping):
        """
        Validate the field mapping for version 2.

        Args:
            field_mapping (dict): The field mapping to validate.

        Raises:
            ValueError: If the field mapping is not valid.
        """
        self._check_non_translated_fields(field_mapping)

        for local_field, field_config in field_mapping.items():
            # Initialize the flags for each local_field
            field_name_defined = False
            field_value_defined = False

            if not isinstance(local_field, str):
                raise ValueError('"local_field_name" must be a string')
            if not isinstance(field_config, dict):
                raise ValueError('"field_config" must be a dictionary')

            for prop, value in field_config.items():
                if prop not in self.valid_props:
                    raise ValueError(f'Invalid property "{prop}" in *_field_mapping. Check: https://github.com/mjanez/ckanext-schemingdcat?tab=field-mapping-structure')
                if prop == 'field_name':
                    field_name_defined = True
                    #log.debug('_is_not_db_key: %s', self._is_not_db_key(local_field, prop, value))
                    self._is_not_db_key(local_field, prop, value)
                    self._check_value(local_field, prop, value)
                if prop == 'field_value':
                    field_value_defined = True
                    self._check_value(local_field, prop, value)
                if prop == 'sort':
                    self._is_not_integer(local_field, prop, value)
                    self._check_value(local_field, prop, value)
                if prop == 'languages':
                    if not isinstance(value, dict):
                        raise ValueError('"languages" must be a dictionary')
                    for lang, lang_config in value.items():
                        if not isinstance(lang, str) or not re.match("^[a-z]{2}$", lang):
                            raise ValueError('Language code must be a 2-letter ISO 639-1 code')
                        if not isinstance(lang_config, dict):
                            raise ValueError('Language config must be a dictionary')
                        for lang_prop, lang_value in lang_config.items():
                            if lang_prop not in self.valid_props:
                                raise ValueError(f'Invalid property "{lang_prop}" in *_field_mapping. Check: https://github.com/mjanez/ckanext-schemingdcat?tab=field-mapping-structure')
                            if lang_prop == 'field_name':
                                field_name_defined = True
                                #log.debug('_is_not_db_key: %s', self._is_not_db_key(local_field, prop, value))
                                self._is_not_db_key(local_field, prop, value)
                                self._check_value(local_field, lang_prop, lang_value)
                            if lang_prop == 'field_value':
                                field_value_defined = True
                                self._check_value(local_field, lang_prop, lang_value)
                            if lang_prop == 'sort':
                                self._is_not_integer(local_field, lang_prop, lang_value)
                                self._check_value(local_field, lang_prop, lang_value)

            # Check the flags after processing each local_field
            if field_name_defined and field_value_defined:
                if field_config.get('field_name') is not None:
                    if not isinstance(field_config.get('field_value'), list):
                        raise ValueError(f'"field_value" for "{local_field}" can only be used if it is a list. First, check that the local_field_name accepts lists, otherwise the harvester validator may have problems.')

        return field_mapping