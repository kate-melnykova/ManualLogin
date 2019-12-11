from abc import ABC, abstractmethod
from datetime import datetime
import json
from time import mktime, time
from typing import List
from uuid import uuid4

# from models.db import search
from models.db import DB
from models.exceptions import NotFound, ValidationError


class BaseField(ABC):
    def __init__(self, default=None):
        # if callable(default):
        #   default = default()
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
        print(f'Converting DateField for db storage: value={value}')
        if value is '' or None:
            return ''
        else:
            return int(mktime(value.timetuple()))

    @staticmethod
    def to_python(timestamp):
        if timestamp == '':
            return ''
        else:
            return datetime.fromtimestamp(timestamp)


class BaseModel(ABC):
    @classmethod
    def get_attributes(cls):
        return ['id', 'date']

    id = TextField(default='')
    date = DateField(default=lambda kwargs: datetime.now())

    @classmethod
    def defaults(cls, **kwargs):
        """
        specify default values of all user attributes.
        :param kwargs: all user data. Please make sure that this data contains username
        """
        data = dict()
        for attribute in cls.get_attributes():
            default = getattr(cls, attribute).default
            if callable(default):
                data[attribute] = default(kwargs)
            else:
                data[attribute] = default
        return data

    @staticmethod
    def _generate_id(**kwargs):
        return uuid4()

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def save(self):
        d = dict()
        for attribute in self.get_attributes():
            print(f'Saving... {attribute}, {getattr(self, attribute)}')
            d[attribute] = getattr(type(self), attribute).to_db(getattr(self, attribute))
        print(f'Data ready for saving: {d}')
        DB.save(self.id, json.dumps(d))

    @classmethod
    def exists(cls, id: str or int) -> bool:
        return DB.exists(id)

    @classmethod
    def load(cls, id: str):
        print(f'Loading: id={id}')
        data = DB.load(id)
        if data is None:
            raise NotFound

        print(f'Loaded data: {data}')
        data = json.loads(data)
        for k, v in data.items():
            data[k] = getattr(cls, k).to_python(v)
        return cls(**data)

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
        instance = cls(**attrs)
        print(f'Data to save {attrs}')
        instance.save()
        return instance

    @staticmethod
    def info_to_db_key(**kwargs) -> str:
        return '*'

    @classmethod
    def search(cls, **kwargs) -> List:
        return list(DB.search(cls.info_to_db_key(**kwargs)))


