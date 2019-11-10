from time import time
import json

import redis

r = redis.Redis()


class BaseUser:
    def __init__(self, username, password='', first_name=None,
                 dob=None, email=None, registration_date=None):
        self.username = username
        self.password = password
        self.first_name = first_name
        self.dob = dob
        self.email = email
        if registration_date is None:
            self.registration_date = time()
        else:
            self.registration_date = registration_date

    def is_authenticated(self):
        raise NotImplemented


class User(BaseUser):
    def is_authenticated(self):
        return True

    @classmethod
    def load(cls, username):
        user_data = json.loads(r.get(username))
        print(f'User data is {user_data}')
        return cls(username, user_data)

    def save(self):
        data = dict()
        attributes = ['username', 'password', 'first_name',
                      'dob', 'email', 'registration_date']
        for attribute in attributes:
            data[attribute] = self.__getattribute__(attribute)
        print(f'User data is {data}')
        r.set(self.username, data)


class AnonymousUser(BaseUser):
    def __init__(self):
        super().__init__('AnonymousUser')

    def is_authenticated(self):
        return False

