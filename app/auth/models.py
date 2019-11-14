from time import time
import json
from passlib.hash import sha256_crypt
from copy import copy
from typing import Dict

from models.db import redis as r
from models.basemodel import BaseModel, ValidationError


class BaseUser(BaseModel):

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
    def defaults(cls, **kwargs) -> Dict[str]:
        """
        specify default values of all user attributes.
        :param kwargs: all user data. Please make sure that this data contains username
        """
        return {
            'id': cls._generate_id(kwargs['username']),
            'password': '',
            'first_name': '',
            'dob': '',
            'email': '',
            'registration_date': int(time()),
        }

    @classmethod
    def get_attributes(cls):
        return list(cls.defaults().keys()) + ['username', 'id']

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
    _attributes = ['username', 'password', 'first_name',
                  'dob', 'email', 'registration_date', 'id']

    is_authenticated = True

    def save(self) -> None:
        data = dict()
        for attribute in self._attributes:
            data[attribute] = self.__getattribute__(attribute)
        print(f'data before saving is {data}')
        r.set(self.id, json.dumps(data))

    def verify_password(self, password: str) -> bool:
        return sha256_crypt.verify(password, self.password)

    @classmethod
    def load(cls, username: str) -> 'User':
        """
        Loads user from redis db 0
        :param username: username, also a key in redis db
        :return: instance of User if username is in db, otherwise raises NotFound
        """
        return super().load(cls._generate_id(username))


class AnonymousUser(BaseUser):
    is_authenticated = False

    def __init__(self):
        super().__init__(username='AnonymousUser')

