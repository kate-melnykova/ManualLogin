from datetime import datetime
import json
from time import mktime
from typing import List

from models.db import search
from models.exceptions import NotFound, ValidationError


class BaseModel:
    @classmethod
    def get_connection(cls):
        from models.db import redis
        return redis

    @classmethod
    def get_attributes(cls):
        return list(cls.defaults().keys())

    @staticmethod
    def _generate_id(**kwargs):
        raise NotImplemented

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def save(self):
        d = dict()
        for attribute in self.get_attributes():
            d[attribute] = getattr(type(self), attribute).to_db(getattr(self, attribute))
        # print(f'Data before saving: {json.dumps(d)}')
        r = self.get_connection()
        r.set(self.id, json.dumps(d))

    @classmethod
    def exists(cls, id: str or int) -> bool:
        r = cls.get_connection()
        return bool(r.exists(id))

    @classmethod
    def load(cls, id: str or int):
        r = cls.get_connection()
        data = r.get(id)
        if data is None:
            raise NotFound

        print(f'Loaded data: {data}')
        data = json.loads(data)
        for k, v in data.items():
            data[k] = getattr(cls, k).to_python(v)
        return cls(**data)

    @classmethod
    def defaults(cls, **kwargs):
        return kwargs

    @classmethod
    def validate(cls, data):
        pass

    @classmethod
    def clean(cls, data):
        return data

    @classmethod
    def create(cls, **kwargs):
        """
        creates new instance or raises ValidationError
        :param kwargs:
        :return:
        """
        cls.validate(kwargs)
        attrs = cls.defaults(**kwargs)
        attrs.update(kwargs)
        cls.clean(attrs)
        print(f'Data to save {attrs}')
        instance = cls(**attrs)
        instance.save()
        return instance

    @staticmethod
    def info_to_db_key(**kwargs) -> str:
        raise NotImplemented

    @classmethod
    def search(cls, **kwargs) -> List:
        db_key = cls.info_to_db_key(**kwargs)
        return [cls.load(key) for key in search(db_key)]


class BaseField:
    def __init__(self, default=None):
        if callable(default):
            default = default()
        self.default = default

    @staticmethod
    def to_python(value):
        return value

    @staticmethod
    def to_db(value):
        return value


class TextField(BaseField):
    pass


class DateField(BaseField):
    @staticmethod
    def to_db(value):
        if value is None:
            return ''
        else:
            return int(mktime(value.timetuple()))

    @staticmethod
    def to_python(timestamp):
        if timestamp == '':
            return None
        else:
            return datetime.fromtimestamp(timestamp)


