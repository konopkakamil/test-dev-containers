from ckanext.keycloak.oauth2 import OAuth2Helper
import pytest
import ckan.model as model
from ckanext.keycloak import usertokentable

oauth2 = OAuth2Helper()

@pytest.fixture
def clear_user_tokens():
    model.Session.query(usertokentable.UserToken).delete()

@pytest.mark.usefixtures('clear_user_tokens')
def test_token_persist():
    username = "test_username"
    access_token = "test_access_token"
    refresh_token = "test_refresh_token"
    token_type = "Bearer"
    expires_in = "300"

    token = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": token_type,
        "expires_in": expires_in
    }

    oauth2.update_token(username, token)
    persisted_token = oauth2.get_stored_token(username)

    assert persisted_token.get('user_name') is None
    assert persisted_token['access_token'] == access_token
    assert persisted_token['refresh_token'] == refresh_token
    assert persisted_token['token_type'] == token_type
    assert persisted_token['expires_in'] == expires_in
    assert type(persisted_token['expires_in']) is str

@pytest.mark.usefixtures('clear_user_tokens')
def test_token_delete():
    username = "test_username"
    access_token = "test_access_token"
    refresh_token = "test_refresh_token"
    token_type = "Bearer"
    expires_in = "300"

    token = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": token_type,
        "expires_in": expires_in
    }

    oauth2.update_token(username, token)
    oauth2.delete_token(username)
    persisted_token = oauth2.get_stored_token(username)

    assert persisted_token is None

@pytest.mark.usefixtures('clear_user_tokens')
def test_token_update():
    username = "test_username"

    token = {
        "access_token": "access_token",
        "refresh_token": "refresh_token",
        "token_type": "token_type",
        "expires_in": "expires_in"
    }

    oauth2.update_token(username, token)
    
    access_token = "test_access_token"
    refresh_token = "test_refresh_token"
    token_type = "Bearer"
    expires_in = "300"

    new_token = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": token_type,
        "expires_in": expires_in
    }

    oauth2.update_token(username, new_token)
    updated_token = oauth2.get_stored_token(username)

    assert updated_token.get('user_name') is None
    assert updated_token['access_token'] == access_token
    assert updated_token['refresh_token'] == refresh_token
    assert updated_token['token_type'] == token_type
    assert updated_token['expires_in'] == expires_in
    assert type(updated_token['expires_in']) is str
