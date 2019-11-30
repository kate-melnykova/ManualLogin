from datetime import datetime
from unittest.mock import patch, Mock, MagicMock

import pytest

from app.app import app
from app.auth.models import User, AnonymousUser
from app.content.models import BlogPost

app.testing = True
@pytest.fixture
def client():
    test_client = app.test_client()
    yield test_client


def test_create_method_returns_a_valid_object(client):
    pass


db_sample_user = b'{"id": "user:username",' \
                 b' "password": "hashed_secret_password",' \
                 b' "first_name": "first name",' \
                 b' "dob": 600000000.0,' \
                 b' "email": "fake_email@email.com",' \
                 b' "registration_date": 1570000000,' \
                 b' "username": "username"}'


@patch('models.db.redis.get', return_value=db_sample_user)
def test_load_user_form_db_returns_object_in_python_format(test_username='test_user'):
    user = User.load(test_username)
    assert isinstance(user.id, str)
    assert isinstance(user.password, str)
    assert isinstance(user.first_name, str)
    assert isinstance(user.dob, datetime)
    assert isinstance(user.email, str)
    assert isinstance(user.registration_date, datetime)
    assert isinstance(user.username, str)


db_sample_blogpost =  b'{"id": "blogpost:sample_id",' \
                      b' "author_id": "user:username",' \
                      b' "title": "Post title",' \
                      b' "content": "Post content",' \
                      b' "author": "username"}'


@patch('models.db.redis.get', return_value=db_sample_blogpost)
def test_load_user_form_db_returns_object_in_python_format(test_post='test_post'):
    post = BlogPost.load(test_post)
    assert isinstance(post.id, str)
    assert isinstance(post.author_id, str)
    assert isinstance(post.title, str)
    # assert isinstance(post.content, ManualType)
    assert isinstance(post.author, str)





