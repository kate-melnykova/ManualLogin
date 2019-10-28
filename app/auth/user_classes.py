class BaseUser:
    def __init__(self, username, info=dict()):
        self.username = username
        for k, v in info.items():
            setattr(self, k, v)

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

