from time import time
import json
from passlib.hash import sha256_crypt
from typing import Dict

from models.basemodel import BaseModel, ValidationError
from models.basemodel import TextField, DateField


class BaseUser(BaseModel):
    id = TextField()
    username = TextField(default='')
    first_name = TextField(default='')
    dob = DateField(default='')
    email = TextField(default='')
    password = TextField(default='')
    registration_date = DateField(default=int(time()))

    @staticmethod
    def _generate_id(**kwargs) -> str:
        """
        generates db primary key
        """
        return f'user:{kwargs["username"]}'

    @staticmethod
    def hash_password(password: str) -> str:
        """
        hashes password using sha256 encrypting
        :param password: password to be hashed
        :return: hashed password
        """
        return sha256_crypt.encrypt(password)

    @staticmethod
    def validate(data: Dict) -> None:
        """
        validates that data contains key username. If not, raises ValidationError
        Function is used to verify that data contains enough info about the user
        :param data: all info about user
        """
        if 'username' not in data:
            raise ValidationError

    @classmethod
    def defaults(cls, **kwargs):
        """
        specify default values of all user attributes.
        :param kwargs: all user data. Please make sure that this data contains username
        """
        return {
            'id': cls._generate_id(username=kwargs.get('username')),
            'username': cls.username.default,
            'password': cls.password.default,
            'first_name': cls.first_name.default,
            'dob': cls.dob.default,
            'email': cls.email.default,
            'registration_date': cls.registration_date.default
        }

    @classmethod
    def get_attributes(cls):
        return list(cls.defaults().keys())

    @staticmethod
    def info_to_db_key(**kwargs) -> str:
        return f'user:{kwargs["username"]}' if 'username' in kwargs else 'user:*'

    @classmethod
    def clean(cls, data: Dict) -> Dict:
        """
        prepares the data for saving
        :param data: dictionary with user info
        :return: dictionary with cleaned user info
        """
        data['password'] = cls.hash_password(data['password'])
        return data

    def verify_password(self, password: str) -> bool:
        """
        verifies that the password matches the hashed password
        :param password: unhashed password
        """
        return False


class User(BaseUser):

    is_authenticated = True

    def save(self) -> None:
        data = dict()
        for attribute in self.get_attributes():
            data[attribute] = self.__getattribute__(attribute)
        print(f'data before saving is {data}')
        r = self.get_connection()
        r.set(self.id, json.dumps(data))

    def verify_password(self, password: str) -> bool:
        return sha256_crypt.verify(password, self.password)

    @classmethod
    def exists(cls, username: str) -> bool:
        """
        checks if the user username is in the database
        """
        r = cls.get_connection()
        return bool(r.exists(cls._generate_id(username=username)))

    @classmethod
    def load(cls, username: str) -> 'User':
        """
        Loads user from redis db 0
        :param username: username, also a key in redis db
        :return: instance of User if username is in db, otherwise raises NotFound
        """
        return super().load(cls._generate_id(username=username))


class AnonymousUser(BaseUser):
    is_authenticated = False

    def __init__(self):
        super().__init__(username='AnonymousUser')

