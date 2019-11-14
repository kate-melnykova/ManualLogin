from time import time
import json
from passlib.hash import sha256_crypt

from models.db import redis as r


class BaseUser:
    @staticmethod
    def _generate_id(username):
        return f'user:{username}'

    def __init__(self, username, password='', first_name=None,
                 dob=None, email=None, registration_date=None, id=None):
        self.username = username
        self.id = id or self._generate_id(username)
        if len(password) > 15:
            self.password = password # password has been hashed earlier
        else:
            self.password = sha256_crypt.encrypt(password)
        print(f'id is {self.id}: user.password is {password} and hashed {self.password}')
        self.first_name = first_name
        self.dob = dob
        self.email = email
        self.registration_date = registration_date or int(time())

    @classmethod
    def load(cls, username: str) -> 'User' or 'AnonymousUser':
        """
        Loads user from redis db 0
        :param username: username, also a key in redis db
        :return: instance of User if username is in db, None otherwise
        """
        data = r.get(cls._generate_id(username))
        return data and User(**json.loads(data)) or AnonymousUser()

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


class AnonymousUser(BaseUser):
    is_authenticated = False

    def __init__(self):
        super().__init__('AnonymousUser')

