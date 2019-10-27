from unittest.mock import patch, MagicMock

import pytest

from app.app import app, get_current_user


@pytest.fixture
def client():
    test_client = app.test_client()
    yield test_client


def test_login_page_redirects_to_logout_when_user_is_authenticated(client):
    with patch('app.get_current_user') as get_current_user_mock:
        response = client.get('/login')
    assert response.status_code == 302
    get_current_user_mock.assert_called_once()


def test_login_page_shows_content_when_user_is_not_authenticated(client):
    with patch('app.get_current_user', return_value=None) as get_current_user_mock:
        response = client.get('/login')
    assert response.status_code == 200
    get_current_user_mock.assert_called_once()


def test_get_current_user_no_encrypted_user_name_in_cookies(client):
    request = MagicMock()
    request.cookies.get = MagicMock(return_value=None)
    assert get_current_user(request) is None
    request.cookies.get.assert_called_once_with('username')


def test_get_current_user_cant_decrypt(client):
    request = MagicMock()
    request.cookies.get = MagicMock(return_value='encrypted string')
    assert get_current_user(request) is None
    request.cookies.get.assert_called_once_with('username')


def test_get_current_user_can_decrypt_but_no_such_user(client):
    from app.app import db
    request = MagicMock()
    with patch.dict(db, {'ivan': {}}, clear=True):
        with patch('app.crypting.aes_decrypt', return_value='user') as aes_decrypt_mock:
            assert get_current_user(request) is None
    request.cookies.get.assert_called_once_with('username')


def test_get_current_user_success(client):
    from app.app import db
    request = MagicMock()
    with patch.dict(db, {'ivan': {}}, clear=True):
        with patch('app.crypting.aes_decrypt', return_value='ivan') as aes_decrypt_mock:
            assert get_current_user(request) == 'ivan'
    request.cookies.get.assert_called_once_with('username')
