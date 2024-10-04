import logging

from ckan.lib.plugins import DefaultTranslation
import ckan.plugins as p

from ckanext.fototeca import helpers, validators, blueprint

try:
    config_declarations = p.toolkit.blanket.config_declarations
except AttributeError:
    # CKAN 2.9 does not have config_declarations.
    # Remove when dropping support.
    def config_declarations(cls):
        return cls

log = logging.getLogger(__name__)

@config_declarations
class FototecaPlugin(p.SingletonPlugin,  DefaultTranslation):
    p.implements(p.IConfigurer)
    p.implements(p.ITemplateHelpers)
    p.implements(p.ITranslation)
    p.implements(p.IValidators)
    p.implements(p.IBlueprint)


    # IConfigurer
    def update_config(self, config_ ):
        p.toolkit.add_template_directory(config_, 'templates')
        p.toolkit.add_public_directory(config_, 'public')
        p.toolkit.add_resource('assets', 'ckanext-fototeca')

    # Blueprints
    def get_blueprint(self):
        return [blueprint.fototeca]

    # Helpers
    def get_helpers(self):
        all_helpers = dict(helpers.all_helpers)
        return all_helpers

    # Validators
    def get_validators(self):
        return dict(validators.all_validators)