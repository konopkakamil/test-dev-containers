import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging

import ckan.model as model

from ckanext.keycloak.views import get_blueprint
from ckanext.keycloak import helpers as h, usertokentable

log = logging.getLogger(__name__)


class KeycloakPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config_):
        log.info('init keycloack plugin')
        usertokentable.create_table(model)

        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('assets', 'keycloak')

    def get_blueprint(self):
        return get_blueprint()
  
    # ITemplateHelpers

    def get_helpers(self):
        return {
            'button_style': h.button_style,
            'enable_internal_login': h.enable_internal_login,
        }
