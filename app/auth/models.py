from time import time
import json
from passlib.hash import sha256_crypt
from copy import copy
from typing import Dict

from models.db import redis as r
from models.basemodel import BaseModel, ValidationError


class BaseUser(BaseModel):
    attributes = ['username', 'password', 'first_name',
                 'dob', 'email', 'registration_date', 'id']

    @staticmethod
    def _generate_id(**kwargs):
        return f'user:{kwargs["username"]}'

    @staticmethod
    def hash_password(password):
        return sha256_crypt.encrypt(password)

    @staticmethod
    def validate(data: Dict):
        if 'username' not in data:
            raise ValidationError

    @classmethod
    def defaults(cls, **kwargs):
        return {
            'id': cls._generate_id(kwargs['username']),
            'password': '',
            'first_name': '',
            'dob': '',
            'email': '',
            'registration_date': int(time()),
        }

    @classmethod
    def clean(cls, data):
        data['password'] = cls.hash_password(data['password'])
        return data

    def verify_password(self, password: str) -> bool:
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
    def load(cls, username: str) -> 'User' or None:
        """
        Loads user from redis db 0
        :param username: username, also a key in redis db
        :return: instance of User if username is in db, None otherwise
        """
        return super().load(cls._generate_id(username))


class AnonymousUser(BaseUser):
    is_authenticated = False

    def __init__(self):
        super().__init__(username='AnonymousUser')

