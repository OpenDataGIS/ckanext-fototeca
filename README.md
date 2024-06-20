# ckanext-fototeca
Extensión que amplía esquemas, cosechadores y temas creada para la Fototeca del CNIG

> [!WARNING] 
> Requiere [mjanez/ckanext-schemingdcat](https://github.com/mjanez/ckanext-schemingdcat), [mjanez/ckanext-dcat](https://github.com/mjanez/ckanext-dcat), [ckan/ckanext-scheming](https://github.com/ckan/ckanext-scheming) y [ckan/ckanext-spatial](https://github.com/ckan/ckanext-spatial) para funcionar adecuadamente.


## Requisitos
Compatibilidad con CKAN:

| Versión de CKAN | ¿Compatible?  |
| --------------- | ------------- |
| 2.9             | en pruebas    |


## Instalación
Para instalar `ckanext-fototeca`:

1. Activar el venv de ckan

     . /usr/lib/ckan/default/bin/activate

2. Clona el repositorio y instalalo en el venv de ckan 

		git clone https://github.com/OpenDataGIS/ckanext-fototeca.git
		cd ckanext-fototeca
		pip install -e .

4. Añadir `fototeca` a la configuración `ckan.plugins` en tu archivo de configuración de CKAN.

5. Reinicia CKAN

## Opciones de configuración
Configura la extensión:

  ```ini
  # Add the plugin to the list of plugins
  ckan.plugins = ... spatial_metadata ... dcat ... schemingdcat ... fototeca
  ```
> [!WARNING] 
> Cuando se utiliza la extensión `fototeca`, `schemingdcat`, `scheming`, `dcat` y `spatial` son necesarias.

## Recolectores
### Recolector SQL
El plugin incluye un recolector para bases de datos locales utilizando los esquemas personalizados proporcionados por `schemingdcat` y `ckanext-scheming`. Este recolector es una subclase del Recolector CKAN proporcionado por `ckanext-schemingdcat` y está diseñado para trabajar con el plugin `schemingdcat` para proporcionar un recolector más versátil y personalizable para las instancias de CKAN.

Para usarlo, necesitas agregar el plugin `fototeca_sql_harvester` a tu archivo de opciones:

  ```ini
	ckan.plugins = harvest schemingdcat schemingdcat_datasets ... schemingdcat_ckan_harvester fototeca_sql_harvester
  ```

El Recolector SQL soporta las siguientes opciones:

### Guía de Generación de Esquemas
Esta guía te ayudará a generar un esquema que sea compatible con nuestro sistema. El esquema es un objeto JSON que define la asignación de campos en tu base de datos a los campos en nuestro sistema.

#### Estructura de mapeo de campos
El `dataset_field_mapping`/`distribution_field_mapping` está estructurado de la siguiente manera (versión multilingüe):

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

* `<schema_field_name>`: El nombre del campo en el esquema CKAN.
  * `<language>`: (Opcional) El código de idioma para campos multilingües. Debe ser un código de idioma válido [ISO 639-1](https://localizely.com/iso-639-1-list/). Ahora está anidado bajo la clave `languages`.
* `<fixed_value>/<fixed_value_list>`: (Opcional) Un valor fijo o una lista de valores fijos que se asignarán al campo para todos los registros.
* **Etiquetas de campo**: Posición del campo o nombre del campo:
  * `<field_name>/<field_name_list>`: (Opcional) El nombre del campo en tu base de datos. Debe estar en el formato `{schema}.{table}.{field}`.

Para campos que no son multilingües, puedes usar directamente `field_name` sin la clave `languages`. Por ejemplo:

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

* `database_type`: El tipo de tu base de datos. Actualmente, solo se soporta `postgres`.
* `credentials`: Las credenciales para conectarte a tu base de datos. Debe incluir el `username`, `password`, `host`, `port`, y `database name`.
* `field_mapping_schema_version`: La versión del esquema de mapeo de campos. Actualmente, solo se soporta la versión `1`.
* `dataset_field_mapping`: La asignación de campos en tu base de datos a los campos en nuestro sistema. Cada campo debe estar en el formato `{schema}.{table}.{field}`.
* Otras propiedades de `ckanext-harvest`/`ckanext-schemingdcat`.

#### Tipos de Campos
Hay dos tipos de campos que pueden ser definidos en la configuración:

1. **Campos regulares**: Estos campos tienen una etiqueta de campo para definir el mapeo o un valor fijo para todos sus registros.
    - **Propiedades**: Un campo puede tener una de estas tres propiedades:
      - **Campos de valor fijo**: Estos campos tienen un valor fijo que se asigna a todos los registros. Esto se define usando la propiedad `field_value`. Si `field_value` es una lista, `field_name` podría establecerse al mismo tiempo, y el `field_value` extiende la lista obtenida del campo remoto.
      - **Etiquetas de campo**: Nombre del campo en la base de datos:
        - **Campos basados en nombre**: Estos campos se definen por su nombre en la tabla DB. Esto se define usando la propiedad `field_name`.
2. **Campos multilingües**: Estos campos tienen diferentes valores para diferentes idiomas. Cada idioma se representa como un objeto separado dentro del objeto de campo (`es`, `en`, ...). El objeto de idioma puede tener propiedades `field_value`, y `field_name`, al igual que un campo normal.

## Validación
El esquema se valida utilizando la clase `SqlFieldMappingValidator`. Esta clase verifica que el esquema esté en el formato correcto y que todos los campos estén en el formato correcto `{schema}.{table}.{field}`. Si el esquema no es válido, se generará un `ValueError`.

Para más información sobre la estructura de mapeo de campos, por favor revisa: [https://github.com/mjanez/ckanext-schemingdcat?tab=field-mapping-structure](https://github.com/mjanez/ckanext-schemingdcat?tab=field-mapping-structure)

## Instalación de desarrollador
Para instalar `ckanext-fototeca `en modo desarrollador ejecuta:

	git clone https://github.com/OpenDataGIS/ckanext-fototeca.git
	cd ckanext-fototeca
	python setup.py develop


## Tests
Para ejecutar los test:
		
	pytest --ckan-ini=test.ini

## Licencia
[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
