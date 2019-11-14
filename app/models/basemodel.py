import json
from uuid import uuid4

from models.db import redis as r


class NotFound(Exception):
    message = 'Entry is not found in the database'


class BseModel:
    attributes = ['id']

    @staticmethod
    def _generate_id():
        raise NotImplemented

    def __init__(self, id=None):
        self.id = id or self._generate_id()

    @classmethod
    def create(cls):
        post = cls()
        post.save()
        return post

    def save(self):
        d = dict()
        for attribute in self.attributes:
            d[attribute] = self.__getattribute__(attribute)
        r.set(id, json.dumps(d))

    @classmethod
    def load(cls, id):
        data = r.get(id)
        if data is None:
            raise NotFound
        return cls(**json.loads(data))
