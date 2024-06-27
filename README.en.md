# ckanext-fototeca
Extension that extends schemes, harvesters and themes created for the CNIG fototeca.

> [!WARNING] 
> Requires [mjanez/ckanext-schemingdcat](https://github.com/mjanez/ckanext-schemingdcat), [mjanez/ckanext-dcat](https://github.com/mjanez/ckanext-dcat), [ckan/ckanext-scheming](https://github.com/ckan/ckanext-scheming) and [ckan/ckanext-spatial](https://github.com/ckan/ckanext-spatial) to function properly.


## Requirements
CKAN compatibility:

| CKAN version | Compatibility?
| --------------- | ------------- |
| 2.9 | in testing |


## Installation
To install `ckanext-fototeca`:

1. Enable ckan's venv.

     . /usr/lib/ckan/default/bin/activate

2. Clone the repository and install it in the ckan venv. 

		git clone https://github.com/OpenDataGIS/ckanext-fototeca.git
		cd ckanext-fototeca
		pip install -e .

4. Add `fototeca` to the `ckan.plugins` configuration in your CKAN configuration file.

5. Restart CKAN

## Configuration options
Configure the extension:

  ```ini
  # Add the plugin to the list of plugins
  ckan.plugins = ... spatial_metadata ... dcat ... schemingdcat ... fototeca
  ```
> [!WARNING] 
> When using the `fototeca` extension, `schemingdcat`, `scheming`, `dcat` and `spatial` are required.

## Collectors
### SQL Collector
The plugin includes a collector for local databases using the custom schemas provided by `schemingdcat` and `ckanext-scheming`. This collector is a subclass of the CKAN Collector provided by `ckanext-schemingdcat` and is designed to work with the `schemingdcat` plugin to provide a more versatile and customisable collector for CKAN instances.

To use it, you need to add the `schemingdcat_sql_harvester` plugin to your options file:

  ```ini
	ckan.plugins = harvest schemingdcat schemingdcat_datasets ... schemingdcat_ckan_harvester fototeca_sql_harvester
  ```

The SQL Harvester supports the following options:

### Schema Generation Guide.
This guide will help you generate a schema that is compatible with our system. The schema is a JSON object that defines the mapping of fields in your database to fields in our system.

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
  * `<language>`: (Optional) The language code for multilingual fields. Must be a valid language code [ISO 639-1](https://localizely.com/iso-639-1-list/). It is now nested under the `<languages` key.
* `<fixed_value>/<fixed_value_list>`: (Optional) A fixed value or a list of fixed values to be assigned to the field for all records.
* Field labels**: Field position or field name:
  * `<field_name>/<field_name_list>`: (Optional) The name of the field in your database. Must be in the format `{schema}.{table}.{field}`.

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
      "alternate_identifier": {
          "field_name": "fototeca.vista_ckan.cod_vuelo",
          "is_p_key": true,
          "index": true,
          "f_key_references": [
              "fototeca.vuelos.cod_vuelo"
          ]
      },
      "flight_color": {
          "field_name": "fototeca.vista_ckan.color",
          "f_key_references": [
              "fototeca.l_color.color"
          ]
      },
      },
      "encoding": {
          "field_value": "UTF-8"
      },
      "title_translated":{
         "languages": {
            "es":{
              "field_name": "fototeca.vuelos.nom_vuelo",
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
* `credentials`: The credentials to connect to your database. Must include the `username`, `password`, `host`, `port`, and `database name`.
* field_mapping_schema_version`: The version of the field mapping schema. Currently, only version `1` is supported.
* `dataset_field_mapping`: The mapping of fields in your database to fields in our system. Each field must be in the format `{schema}.{table}.{field}`.
* Other properties of `ckanext-harvest`/`ckanext-schemingdcat`.

#### Field Types
There are two types of fields that can be defined in the configuration:

1. **Regular fields**: These fields have a field label to define the mapping or a fixed value for all your records.
    - Properties**: A field can have one of three properties:
      - **Fixed value fields (`field_value`)**: These fields have a fixed value that is assigned to all records. This is defined using the `field_value` property. If `field_value` is a list, `field_name` could be set at the same time, and the `field_value` extends the list obtained from the remote field.
      - Field tags: Name of the field in the database:
        - **Fields based on name (`field_name`)**: These fields are defined by their name in the DB table. This is defined using the `field_name` property. To facilitate the retrieval of data from the database, especially with regard to the identification of primary keys (`p_key`) and foreign keys (`f_key`), the following properties can be added to the `field_mapping` schema:
          1. **Field is primary key (`is_p_key`)** [*Optional*]: This property will identify whether the field is a primary key (`p_key`) or not if not specified. This will facilitate join operations and references between tables.
          2. **Table references (`f_key_references`)** [*Optional* (`list`)] For fields that are foreign keys, this property would specify which schemas, tables and fields the foreign key refers to. For example, `["public.flight.id", "public.camera.id"]`. This is useful for automating joins between tables.
          3. **Index (`index`)** [*Optional*]: A boolean property to indicate whether the field should be indexed to improve query efficiency. Although not specific to primary or foreign keys, it is relevant for query optimisation. The default value is `false`.

          The modified schema would allow more efficient data retrieval and simplify DataFrame construction, especially in complex scenarios with multiple tables and relationships. Here is an example of what the modified schema would look like for a field that is a foreign key:

          ```json
          "dataset_field_mapping": {
            "alternate_identifier": {
                "field_name": "photo library.view_ckan.flight_code",
                "is_p_key": true,
                "index": true,
                "f_key_references": [
                    "photo library.flights.flight_code".
                ]
            }
          }
          ```

2. **Multilingual fields (`languages`): These fields have different values for different languages. Each language is represented as a separate object within the field object (`is`, `en`, ...). The language object can have `field_value`, and `field_name` properties, just like a normal field.

## Validation
The schema is validated using the `SqlFieldMappingValidator` class. This class checks that the schema is in the correct format and that all fields are in the correct `{schema}.{table}.{field}` format. If the schema is not valid, a `ValueError` will be generated.

For more information on the field mapping structure, please see: [https://github.com/mjanez/ckanext-schemingdcat?tab=field-mapping-structure](https://github.com/mjanez/ckanext-schemingdcat?tab=field-mapping-structure)

## Developer installation
To install `ckanext-photo library` in developer mode run:

	git clone https://github.com/OpenDataGIS/ckanext-fototeca.git
	cd ckanext-photo library
	python setup.py develop


## Tests
To run the tests:
		
	pytest --ckan-ini=test.ini

## License
[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)