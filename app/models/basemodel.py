import json

from models.db import redis as r


class NotFound(Exception):
    message = 'Entry is not found in the database'


class ValidationError(ValueError):
    message = 'Inappropriate arguments'


class BaseModel:
    attributes = []

    @classmethod
    def _attributes(cls):
        return list(set(cls.attributes + ['id']))

    @staticmethod
    def _generate_id(**kwargs):
        raise NotImplemented

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__setattr__(k, v)
        self.id = kwargs.get('id') or self._generate_id(**kwargs)

    def save(self):
        d = dict()
        for attribute in self._attributes():
            d[attribute] = self.__getattribute__(attribute)
        r.set(self.id, json.dumps(d))

    @classmethod
    def load(cls, id):
        data = r.get(id)
        if data is None:
            raise NotFound
        return cls(**json.loads(data))

    @classmethod
    def defaults(cls, **kwargs):
        return kwargs

    @classmethod
    def clean(cls, data):
        return data

    @classmethod
    def create(cls, **kwargs):
        cls.validate(kwargs)
        attrs = cls.defaults(**kwargs)
        attrs.update(kwargs)
        cls.clean(kwargs)
        instance = cls(**attrs)
        instance.save()
        return instance
