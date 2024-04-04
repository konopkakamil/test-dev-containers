import ckan.model as model

from ckanext.keycloak import usertokentable

class OAuth2Helper(object):

    def get_stored_token(self, user_name):
        user_token = usertokentable.UserToken.by_user_name(user_name=user_name)
        if user_token:
            return {
                'access_token': user_token.access_token,
                'refresh_token': user_token.refresh_token,
                'expires_in': user_token.expires_in,
                'token_type': user_token.token_type
            }
        
    def update_token(self, user_name, token):
        user_token = usertokentable.UserToken.by_user_name(user_name=user_name)

        if not user_token:
            user_token = usertokentable.UserToken()
            user_token.user_name = user_name

        user_token.access_token = token['access_token']
        user_token.token_type = token['token_type']
        user_token.refresh_token = token.get('refresh_token')
        user_token.expires_in = token['expires_in']

        model.Session.add(user_token)
        model.Session.commit()

    def delete_token(self, user_name):
        usertokentable.UserToken.delete(user_name=user_name)
        model.Session.commit()

    