# routingSQL
Librería para interaccionar con bases de datos y relacionar las tablas de manera automática

Actua como un wrapper para sqlalchemy y multiples librerias para simplificar la interacción con bases de datos SQL
Pensado para funcionar con https://github.com/OpenDataGIS/ckanext-fototeca
## Instanciar la librería
### Para based de datos postgres
```python
from sql_routing_pg import routingPG
database = routingPG(user: str, password: str, url: str, port: int, database: str)
```

## Descripción de funciones
### get_columns
```python
get_columns(wanted_columns[])
```
Obten una tabla con las columnas solicitadas.
las columnas tienen que estar en el formato:
```python
wanted_columns = ["schema1.tabla1.columna1","schema1.tabla1.columna2","schema1.tabla2.columna3","schema2.tabla3.columna4"]
```
la función unirá automaticamente las tablas entre sí para generar la tabla.
Por defecto usa "left join" para unir las tablas

### get_schema
```python
get_schema()
```
devuelve la estructura de tablas de la base de datos 

## get_relations
```pythons
get_relations()
```
devuelve la estructura de tablas de la base de datos 

## Extender funcionalidad para implementar otros tipos de bases de datos
extender sql_routing_base, tal que
```python
from ckanext.fototeca.lib.routingSQL.sql_routing_base import routingBase

class routingPG(routingBase):
```

y incluir un `__init__()` para generar `_engine, _schema y _relation` 
el formato de `_schema` debe ser:
```
{schema:{
        table : [
                table1,
                table2,
                table3,
                table4,
                ...
                ]
        },table1 : [
                ...
                ]
        },
schema2 :{
        table : [
                ...
                ]
        },table1 : [
                ...
                ]
        },
        ...
...
}
```

el formato de `_schema` debe ser:
```
{table1:{
        foreignTable1 : {
            key1:key2,
            ...
        },
        foreignTable2 : {
            key1:key2,
            ...
        },
table2:{
        foreignTable1 : {
            key1:key2,
            ...
        },
        foreignTable3 : {
            key1:key2,
            ...
        }
...
```
donde key1 es la clave en la primera tabla, y key2 es la clave en la segunda tabla

`_engine` tiene que ser un engine de SQLalchemy instanciado con el tipo de base de datos deseada.
