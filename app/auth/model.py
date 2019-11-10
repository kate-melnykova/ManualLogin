import datetime
import redis

r = redis.Redis()

class BaseUser:
    def __init__(self, username, password, first_name=None,
                 dob=None, email=None, registration_date=None):
        self.username = username
        self.password = password
        self.first_name = first_name
        self.dob = dob
        self.email = email
        if registration_date is None:
            self.registration_date = datetime.now()
        else:
            self.registration_date = registration_date

    def is_authenticated(self):
        raise NotImplemented


class User(BaseUser):
    def is_authenticated(self):
        return True


class AnonymousUser(BaseUser):
    def __init__(self):
        super().__init__('AnonymousUser')

    def is_authenticated(self):
        return False

