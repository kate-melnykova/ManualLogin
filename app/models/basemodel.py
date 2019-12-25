from abc import ABC, abstractmethod
from datetime import datetime
import json
from time import mktime, time
from typing import List
from uuid import uuid4

# from models.db import search
from models.db import db
from models.exceptions import NotFound, ValidationError


class BaseField(ABC):
    __slots__ = ['default', 'value']

    def __init__(self, name: str, default=None):
        self.name = '_' + name
        #if callable(default):
        #    self.default = default()
        self.default = default

    def __set__(self, instance, value):
        setattr(instance, self.name, value)

    def __get__(self, instance, owner=None):
        return getattr(instance, self.name, self.default)

    def to_db(self, instance):
        return self.__get__(instance)

    @staticmethod
    def to_python(value):
        return value

    """
    def clone(self):
        instance = self.__class__(default=self.default)
        instance.value = self.value
        return instance
    """


class TextField(BaseField):
    pass


class DateField(BaseField):
    def to_db(self, instance):
        raw_value = self.__get__(instance)
        if raw_value is '' or None:
            return ''
        else:
            return int(mktime(raw_value.timetuple()))

    @staticmethod
    def to_python(timestamp):
        if timestamp == '':
            return ''
        else:
            return datetime.fromtimestamp(timestamp)


class BaseModel(ABC):
    @classmethod
    def get_attributes(cls):
        return [attr for attr, value in cls.__dict__.items() if isinstance(value, BaseField)]

    id = TextField(name='id', default='')
    date = DateField(name='date', default=lambda kwargs: datetime.now())

    @staticmethod
    def _generate_id(**kwargs):
        return uuid4()

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def save(self):
        d = dict()
        for attribute in self.get_attributes():
            d[attribute] = type(self).__dict__[attribute].to_db(self)
        print(f'Preparing instance for saving... data={d}')
        db.save(self.id, json.dumps(d))

    @classmethod
    def exists(cls, id: str or int) -> bool:
        return db.exists(id)

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
        attrs = dict(kwargs)
        for attribute in cls.get_attributes():
            if attribute not in kwargs:
                default = getattr(cls, attribute)
                if callable(default):
                    attrs[attribute] = default(kwargs)
                else:
                    attrs[attribute] = default
        cls.clean(attrs)
        print(f'Creating instance with attributes {attrs}')
        instance = cls(**attrs)
        instance.save()
        return instance

    @staticmethod
    def info_to_db_key(**kwargs) -> str:
        return '*'

    @classmethod
    def _db_dict_to_instance(cls, data: bytearray):
        data = json.loads(data)
        data_new = {}
        for k, v in data.items():
            data_new[k] = cls.__dict__[k].to_python(v)
        print(f'Converted data to python: {data_new}')
        instance = cls(**data_new)
        print('Created instance')
        print(instance)
        return cls(**data_new)

    @classmethod
    def load(cls, id: str):
        data = db.load(id)
        if data is None:
            raise NotFound

        return cls._db_dict_to_instance(data)

    @classmethod
    def search(cls, **kwargs) -> iter:
        final_ans = []
        for post in db.search(cls.info_to_db_key(**kwargs)):
            final_ans.append(cls._db_dict_to_instance(post))
        return final_ans

    def delete(self):
        db.delete(self.id)

