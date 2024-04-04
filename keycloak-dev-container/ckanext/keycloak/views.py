import logging
from flask import Blueprint
from ckan.plugins import toolkit as tk
import ckan.lib.helpers as h
import ckan.model as model
from ckan.common import g
from ckan.views.user import set_repoze_user, RequestResetView
from ckanext.keycloak.keycloak import KeycloakClient
import ckanext.keycloak.helpers as helpers
from os import environ

from ckanext.keycloak.oauth2 import OAuth2Helper

log = logging.getLogger(__name__)

keycloak = Blueprint('keycloak', __name__, url_prefix='/user')
oauth2 = OAuth2Helper()

server_url = tk.config.get('ckanext.keycloak.server_url', environ.get('CKANEXT__KEYCLOAK__SERVER_URL'))
client_id = tk.config.get('ckanext.keycloak.client_id', environ.get('CKANEXT__KEYCLOAK__CLIENT_ID'))
realm_name = tk.config.get('ckanext.keycloak.realm_name', environ.get('CKANEXT__KEYCLOAK__REALM_NAME'))
redirect_uri = tk.config.get('ckanext.keycloak.redirect_uri', environ.get('CKANEXT__KEYCLOAK__REDIRECT_URI'))
client_secret_key = tk.config.get('ckanext.keycloak.client_secret_key', environ.get('CKANEXT__KEYCLOAK__CLIENT_SECRET_KEY'))

client = KeycloakClient(server_url, client_id, realm_name, client_secret_key)

def _log_user_into_ckan(resp):
    """ Log the user into different CKAN versions.
    CKAN 2.10 introduces flask-login and login_user method.
    CKAN 2.9.6 added a security change and identifies the user
    with the internal id plus a serial autoincrement (currently static).
    CKAN <= 2.9.5 identifies the user only using the internal id.
    """
    if tk.check_ckan_version(min_version="2.10"):
        from ckan.common import login_user
        login_user(g.user_obj)
        return

    if tk.check_ckan_version(min_version="2.9.6"):
        user_id = "{},1".format(g.user_obj.id)
    else:
        user_id = g.user
    set_repoze_user(user_id, resp)

    log.info(u'User {0}<{1}> logged in successfully'.format(g.user_obj.name, g.user_obj.email))

def sso():
    log.info("SSO Login")
    auth_url = None
    try:
        auth_url = client.get_auth_url(redirect_uri=redirect_uri)
    except Exception as e:
        log.error("Error getting auth url: {}".format(e))
        return tk.abort(500, "Error getting auth url: {}".format(e))
    return tk.redirect_to(auth_url)

def sso_login():
    data = tk.request.args
    token = client.get_token(data['code'], redirect_uri)
    userinfo = client.get_user_info(token)

    if userinfo:
        user_dict = {
            'name': helpers.ensure_unique_username_from_email(userinfo['preferred_username']),
            'email': userinfo['email'],
            'password': helpers.generate_password(),
            'fullname': userinfo['name'],
            'plugin_extras': {
                'idp': 'google'
            }
        }
        context = {"model": model, "session": model.Session}
        g.user_obj = helpers.process_user(user_dict)
        g.user = g.user_obj.name
        context['user'] = g.user
        context['auth_user_obj'] = g.user_obj

        oauth2.update_token(g.user_obj.name, token)

        response = tk.redirect_to(tk.url_for('user.me', context))

        _log_user_into_ckan(response)
        log.info("Logged in success")
        return response
    else:
        return tk.redirect_to(tk.url_for('user.login'))
    
def reset_password():
    email = tk.request.form.get('user', None)
    if '@' not in email:
        log.info(f'User requested reset link for invalid email: {email}')
        h.flash_error('Invalid email address')
        return tk.redirect_to(tk.url_for('user.request_reset'))
    user = model.User.by_email(email)
    if not user:
        log.info(u'User requested reset link for unknown user: {}'.format(email))
        return tk.redirect_to(tk.url_for('user.login'))
    user_extras = user[0].plugin_extras
    if user_extras and user_extras.get('idp', None) == 'google':
        log.info(u'User requested reset link for google user: {}'.format(email))
        h.flash_error('Invalid email address')
        return tk.redirect_to(tk.url_for('user.login'))
    return RequestResetView().post()

def sso_logout(): 
        token = oauth2.get_stored_token(g.user)

        if token:
            try:
                client.logout(token['refresh_token'])
            except Exception as e:
                log.info('Exception occurred: {}'.format(e))
            finally:
                oauth2.delete_token(g.user)
        
        from ckan.common import logout_user
        logout_user()

        return h.redirect_to('user.logged_out_page')

keycloak.add_url_rule('/sso', view_func=sso)
keycloak.add_url_rule('/sso_login', view_func=sso_login)
keycloak.add_url_rule('/sso_logout', view_func=sso_logout)
keycloak.add_url_rule('/reset_password', view_func=reset_password, methods=['POST'])

def get_blueprint():
    return keycloak