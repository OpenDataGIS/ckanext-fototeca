# ckanext-fototeca
Extension that extends the schemes, harvesters and themes created for the CNIG Digital Fototeca

> [!WARNING] 
> Requires [mjanez/ckanext-schemingdcat](https://github.com/mjanez/ckanext-schemingdcat), [mjanez/ckanext-dcat](https://github.com/mjanez/ckanext-dcat), [ckan/ckanext-scheming](https://github.com/ckan/ckanext-scheming) and [ckan/ckanext-spatial](https://github.com/ckan/ckanext-spatial) to work properly.


## Requirements
Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
| 2.9             | yes           |


## Installation
To install the `ckanext-photo library':

1. Activate ckan's venv.

     . /usr/lib/ckan/default/bin/activate

2. Clone the repository and install it into ckan's venv. 

		git clone https://github.com/OpenDataGIS/ckanext-fototeca.git
		cd ckanext-fototeca
		pip install -e .

4. Add `fototeca` to the `ckan.plugins` configuration in your CKAN configuration file.

5. Restart CKAN



## Configuration:

  ```ini
  # Add the plugin to the list of plugins
  ckan.plugins = ... spatial_metadata ... dcat ... schemingdcat ... photo library
  ```
> [!WARNING] 
> When using the `fototeca` extension, `schemingdcat`, `scheming`, `dcat` and `spatial` are required.

## Harvesters
### SQL Harvester
The plugin includes a harvester for local databases using the custom schemas provided by `schemingdcat` and `ckanext-scheming`. This harvester is a subclass of the CKAN Harvester provided by `ckanext-schemingdcat` and is designed to work with the `schemingdcat` plugin to provide a more versatile and customizable harvester for CKAN instances.

To use it, you need to add the `fototeca_sql_harvester` plugin to your options file:

  ```ini
	ckan.plugins = harvest schemingdcat schemingdcat_datasets ... schemingdcat_ckan_harvester fototeca_sql_harvester
  ```

SQL Harvester supports the following options:

### Schema Generation Guide
This guide will help you generate a schema that is compatible with our system. The schema is a JSON object that defines the mapping of fields in your database to the fields in our system.

#### Field mapping structure
The `dataset_field_mapping`/`distribution_field_mapping` is structured as follows (multilingual version):

```json
{
  ...
  "field_mapping_schema_version": 1,
  "<dataset_field_mapping>/<distribution_field_mapping>": {
    "<schema_field_name>": {
      "languages": {
        "<language>":  {
          <"field_value": "<fixed_value>/<fixed_value_list>">,/<"field_name": "<db_field_name>/<db_field_name_list>">
        },
        ...
      },
      ...
    },
    ...
  }
}
```

* `<schema_field_name>`: The name of the field in the CKAN schema.
  * `<language>`: (Optional) The language code for multilingual fields. This should be a valid [ISO 639-1 language code](https://localizely.com/iso-639-1-list/). This is now nested under the `languages` key.
* `<fixed_value>/<fixed_value_list>`: (Optional) A fixed value or a list of fixed values that will be assigned to the field for all records.
* **Field labels**: Field position or field name:
  * `<field_name>/<field_name_list>`: (Optional) The name of the field in your database. It should be in the format `{schema}.{table}.{field}`.

For fields that are not multilingual, you can directly use `field_name` without the `languages` key. For example:

```json
{
  ...
  "field_mapping_schema_version": 2,
  "<dataset_field_mapping>/<distribution_field_mapping>": {
    "<schema_field_name>": {
      <"field_value": "<fixed_value>/<fixed_value_list>">,/<"field_name": "<db_field_name>/<db_field_name_list>">
    },
    ...
  }
}
```

```json
{
   "database_type":"postgres",
   "credentials":{
      "user":"u_fototeca",
      "password":"u_fototeca",
      "host":"localhost",
      "port":5432,
      "db":"fototeca"
   },
   "field_mapping_schema_version":1,
   "dataset_field_mapping":{
      "alternate_identifer":{
         "field_name":"fototeca.vista_ckan.cod_vuelo",
         "sort":2
      },
      "title_translated":{
         "languages": {
            "es":{
               "field_name":"fototeca.vuelos.nom_vuelo",
               "sort":3
            }
         }
      }
   },
   "defaults_groups":[

   ],
   "defaults_tags":[

   ],
   "default_group_dicts":[

   ]
}
```

* `database_type`: The type of your database. Currently, only `postgres` is supported.
* `credentials`: The credentials to connect to your database. It should include the `username`, `password`, `host`, `port`, and `database name`.
* `field_mapping_schema_version`: The version of the field mapping schema. Currently, only version `1` is supported.
* `dataset_field_mapping`: The mapping of fields in your database to the fields in our system. Each field should be in the format `{schema}.{table}.{field}`.
* Other `ckanext-harvest`/`ckanext-schemingdcat` properties.

#### Field Types
There are two types of fields that can be defined in the configuration:

1. **Regular fields**: These fields have a field label to define the mapping or a fixed value for all its records.
    - **Properties**: A field can have one of these three properties:
      - **Fixed value fields**: These fields have a fixed value that is assigned to all records. This is defined using the `field_value` property. If `field_value` is a list, `field_name` could be set at the same time, and the `field_value` extends the list obtained from the remote field.
      - **Field labels**: Database field name:
        - **Name based fields**: These fields are defined by their name in the DB Table. This is defined using the `field_name` property.
2. **Multilingual Fields**: These fields have different values for different languages. Each language is represented as a separate object within the field object (`es`, `en`, ...). The language object can have `field_value`, and `field_name` properties, just like a normal field.

## Validation
The schema is validated using the `SqlFieldMappingValidator` class. This class checks that the schema is in the correct format and that all fields are in the correct `{schema}.{table}.{field}` format. If the schema is not valid, a `ValueError` will be raised.

For more information about the field mapping structure, please check: [https://github.com/mjanez/ckanext-schemingdcat?tab=field-mapping-structure](https://github.com/mjanez/ckanext-schemingdcat?tab=field-mapping-structure)

## Instalación de desarrollador
To install `ckanext-fototeca` for development, activate your CKAN virtualenv and
do:

    git clone https://github.com/keitaroinc/ckanext-fototeca.git
    cd ckanext-fototeca
    python setup.py develop
    pip install -r dev-requirements.txt


## Tests
To run the tests, do:

    pytest --ckan-ini=test.ini

## Licencia
[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
