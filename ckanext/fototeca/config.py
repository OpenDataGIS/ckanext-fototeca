# Vars and configs for ckanext-fototeca

ign_base_url = "https://www.ign.es/web/ign/portal"

# postgres harvester
postgres_geojson_chars_limit = 1000
postgres_geojson_tolerance = 0.001

# Dataset default values
FOTOTECA_HARVESTER_MD_CONFIG = {
    'access_rights': 'http://inspire.ec.europa.eu/metadata-codelist/LimitationsOnPublicAccess/noLimitations',
    'conformance': [
        'http://inspire.ec.europa.eu/documents/inspire-metadata-regulation','http://inspire.ec.europa.eu/documents/commission-regulation-eu-no-13122014-10-december-2014-amending-regulation-eu-no-10892010-0'
    ],
    'author': 'ckanext-fototeca',
    'author_email': 'admin@{ckan_instance}',
    'author_url': '{ckan_instance}/organization/test',
    'author_uri': '{ckan_instance}/organization/test',
    'contact_name': 'Centro Nacional de Información Geográfica (CNIG)',
    'contact_email': 'consulta@cnig.es',
    'contact_url': 'https://www.cnig.es',
    'contact_uri': 'http://datos.gob.es/recurso/sector-publico/org/Organismo/E00125901"',
    'dcat_type': {
        'series': 'http://inspire.ec.europa.eu/metadata-codelist/ResourceType/series',
        'dataset': 'http://inspire.ec.europa.eu/metadata-codelist/ResourceType/dataset',
        'spatial_data_service': 'http://inspire.ec.europa.eu/metadata-codelist/ResourceType/service',
        'default': 'http://inspire.ec.europa.eu/metadata-codelist/ResourceType/dataset',
        'collection': 'http://purl.org/dc/dcmitype/Collection',
        'event': 'http://purl.org/dc/dcmitype/Event',
        'image': 'http://purl.org/dc/dcmitype/Image',
        'still_image': 'http://purl.org/dc/dcmitype/StillImage',
        'moving_image': 'http://purl.org/dc/dcmitype/MovingImage',
        'physical_object': 'http://purl.org/dc/dcmitype/PhysicalObject',
        'interactive_resource': 'http://purl.org/dc/dcmitype/InteractiveResource',
        'service': 'http://purl.org/dc/dcmitype/Service',
        'sound': 'http://purl.org/dc/dcmitype/Sound',
        'software': 'http://purl.org/dc/dcmitype/Software',
        'text': 'http://purl.org/dc/dcmitype/Text',
    },
    'encoding': 'UTF-8',
    'frequency' : 'http://publications.europa.eu/resource/authority/frequency/ANNUAL_3',
    'inspireid_theme': 'OI',
    'language': 'http://publications.europa.eu/resource/authority/language/SPA',
    'license': 'http://creativecommons.org/licenses/by/4.0/',
    'license_id': 'cc-by',
    'lineage_process_steps': 'ckanext-fototeca lineage process steps.',
    'maintainer': 'ckanext-fototeca',
    'maintainer_email': 'admin@{ckan_instance}',
    'maintainer_url': '{ckan_instance}/organization/test',
    'maintainer_uri': '{ckan_instance}/organization/test',
    'metadata_profile': [
        "http://semiceu.github.io/GeoDCAT-AP/releases/2.0.0","http://inspire.ec.europa.eu/document-tags/metadata","https://semiceu.github.io/DCAT-AP/releases/3.0.0"
    ],
    'notes_translated': {
        'es': 'Metadatos del conjunto de datos',
        'en': 'Dataset metadata.'
    },
    'provenance': 'ckanext-fototeca provenance statement.',
    'publisher_name': 'Centro Nacional de Información Geográfica (CNIG)',
    'publisher_email': 'consulta@cnig.es',
    'publisher_url': 'https://www.cnig.es',
    'publisher_identifier': 'http://datos.gob.es/recurso/sector-publico/org/Organismo/E00125901"',
    'publisher_uri': 'https://iepnb.es/catalogo/organization/iepnb',
    'publisher_type': 'http://purl.org/adms/publishertype/NationalAuthority',
    'reference_system': 'http://www.opengis.net/def/crs/EPSG/0/4258',
    'representation_type': {
        'wfs': 'http://inspire.ec.europa.eu/metadata-codelist/SpatialRepresentationType/vector',
        'wcs': 'http://inspire.ec.europa.eu/metadata-codelist/SpatialRepresentationType/grid',
        'default': 'http://inspire.ec.europa.eu/metadata-codelist/SpatialRepresentationType/vector',
        'grid': 'http://inspire.ec.europa.eu/metadata-codelist/SpatialRepresentationType/grid',
        'vector': 'http://inspire.ec.europa.eu/metadata-codelist/SpatialRepresentationType/vector',
        'textTable': 'http://inspire.ec.europa.eu/metadata-codelist/SpatialRepresentationType/textTable',
        'tin': 'http://inspire.ec.europa.eu/metadata-codelist/SpatialRepresentationType/tin',
        'stereoModel': 'http://inspire.ec.europa.eu/metadata-codelist/SpatialRepresentationType/stereoModel',
        'video': 'http://inspire.ec.europa.eu/metadata-codelist/SpatialRepresentationType/video',
    },
    'resources': {
        'availability': 'http://publications.europa.eu/resource/authority/planned-availability/AVAILABLE',
        'name': {
            'es': 'Distribución {format}',
            'en': 'Distribution {format}'
        },
    },
    'rights': 'http://inspire.ec.europa.eu/metadata-codelist/LimitationsOnPublicAccess/noLimitations',
    'spatial': None,
    'spatial_uri': 'http://datos.gob.es/recurso/sector-publico/territorio/Pais/España',
    'status': 'http://purl.org/adms/status/UnderDevelopment',
    'temporal_start': None,
    'temporal_end': None,
    'theme': 'http://inspire.ec.europa.eu/theme/oi',
    'theme_es': 'http://datos.gob.es/kos/sector-publico/sector/medio-ambiente',
    'theme_eu': 'http://publications.europa.eu/resource/authority/data-theme/TECH',
    'topic': 'http://inspire.ec.europa.eu/metadata-codelist/TopicCategory/imageryBaseMapsEarthCover',
    'valid': None
}

FOTOTECA_PUBLISHER_TYPES = {
    'national_authority': {
        'label': 'ministerio',
        'value': 'http://purl.org/adms/publishertype/NationalAuthority'
    },
    'regional_authority': {
        'label': 'consejeria',
        'value': 'http://purl.org/adms/publishertype/RegionalAuthority'
    },
    'local_authority': {
        'label': 'concejalia',
        'value': 'http://purl.org/adms/publishertype/LocalAuthority'
    }
}

FOTOTECA_CODELIST_MAPPING = {
    'flight_color': [
        {
            'value': 'b-n',
            'accepted_values': [
                'B/N',
                'b/n'
            ],
            'pattern': r'^[Bb][/-_][Nn]$'
        }
    ],
    'flight_type': [
        {
            'value': 'analogico',
            'accepted_values': [
                'analógico',
                'analogico'
            ],
            'pattern': r'^[Aa]nal[oó]gico$'
        }
    ],
}