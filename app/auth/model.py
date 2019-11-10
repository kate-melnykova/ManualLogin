from time import time
import json

import redis


r = redis.Redis.from_url(url=f'redis://redis:6379/0')


class BaseUser:
    def __init__(self, username, password='', first_name=None,
                 dob=None, email=None, registration_date=None):
        self.username = username
        self.password = password
        self.first_name = first_name
        self.dob = dob
        self.email = email
        if registration_date is None:
            self.registration_date = int(time())
        else:
            self.registration_date = registration_date
        self._is_authenticated = False

    @classmethod
    def load(cls, username: str) -> 'User' or 'AnonymousUser':
        """
        Loads user from redis db 0
        :param username: username, also a key in redis db
        :return: instance of User if username is in db, None otherwise
        """
        user_data = r.get(username)
        return user_data and User(**json.loads(user_data)) or AnonymousUser()

    def _check_password(self, password):
        return self.password == password

    def is_authenticated(self):
        raise NotImplemented


class User(BaseUser):
    attributes = ['username', 'password', 'first_name',
                  'dob', 'email', 'registration_date']

    def save(self):
        data = dict()
        for attribute in self.attributes:
            data[attribute] = self.__getattribute__(attribute)
        print(f'User data is {data}')
        r.set(self.username, json.dumps(data))

    def authenticate(self, password: str) -> bool:
        self._is_authenticated = self._check_password(password)

    def is_authenticated(self):
        return self._is_authenticated


class AnonymousUser(BaseUser):
    def __init__(self):
        super().__init__('AnonymousUser')

    def authenticate(self):
        pass

    def is_authenticated(self):
        return False

