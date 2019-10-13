from unittest.mock import patch

import pytest

from app import app


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
