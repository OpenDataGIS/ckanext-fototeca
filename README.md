# ckanext-fototeca

Extensión de temas creada para la fototeca del CNIG


## Requisitos

Compatibilidad con CKAN:

| Versión de CKAN | ¿Compatible?  |
| --------------- | ------------- |
| 2.6 o antes     | no probado    |
| 2.7             | no probado    |
| 2.8             | no probado    |
| 2.9             | no probado    |


## Installation

**TODO:** Add any additional install steps to the list below.
   For example installing any non-Python dependencies or adding any required
   config settings.

Para instalar ckanext-fototeca:

1. Activar el venv de ckan

     . /usr/lib/ckan/default/bin/activate

2. Clone the source and install it on the virtualenv

		git clone https://github.com/OpenDataGIS/ckanext-fototeca.git
		cd ckanext-fototeca
		pip install -e .
		pip install -r requirements.txt

4. Añadir `fototeca` a la configuración `ckan.plugins` en tu archivo de configuración de CKAN.

5. Reinicia CKAN

     sudo service apache2 reload


## Opciones de configuración

Ninguna por ahora

## Instalación de desarrollador

Para instalar ckanext-fototeca en modo desarrollador ejecuta:

	git clone https://github.com/OpenDataGIS/ckanext-fototeca.git
	cd ckanext-fototeca
	python setup.py develop
	pip install -r dev-requirements.txt


## Tests

Para ejecutar los test:
		
	pytest --ckan-ini=test.ini

## Licencia

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
