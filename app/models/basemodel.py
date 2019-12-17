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

    def __init__(self, default=None):
        # if callable(default):
        #   default = default()
        self.default = default
        self.value = default

    @staticmethod
    def to_python(value):
        return value

    def to_db(self):
        return self.value

    def clone(self):
        instance = self.__class__(default=self.default)
        instance.value = self.value
        return instance


class TextField(BaseField):
    pass


class DateField(BaseField):
    def to_db(self):
        if self.value is '' or None:
            return ''
        else:
            return int(mktime(self.value.timetuple()))

    @staticmethod
    def to_python(timestamp):
        if timestamp == '':
            return ''
        else:
            return datetime.fromtimestamp(timestamp)


class BaseModel(ABC):
    @classmethod
    def get_attributes(cls):
        return [attr for attr in dir(cls) if isinstance(getattr(cls, attr), BaseField)]

    def __getattribute__(self, name, get_field=False):
        cur_value = object.__getattribute__(self, name)
        if not get_field and isinstance(cur_value, BaseField):
            return cur_value.value

        return cur_value

    def __setattr__(self, name, value):
        try:
            cur_value = object.__getattribute__(self, name)
        except AttributeError:
            self.__dict__[name] = value
        else:
            if isinstance(cur_value, BaseField):
                cur_value = cur_value.clone()
                cur_value.value = value
                self.__dict__[name] = cur_value
                # setattr(self, name, cur_value)
            else:
                self.__dict__[name] = value
                # setattr(self, name, value)

    id = TextField(default='')
    date = DateField(default=lambda kwargs: datetime.now())

    @staticmethod
    def _generate_id(**kwargs):
        return uuid4()

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def save(self):
        d = dict()
        for attribute in self.get_attributes():
            d[attribute] = self.__getattribute__(attribute, get_field=True).to_db()
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
                default = getattr(cls, attribute).default
                if callable(default):
                    attrs[attribute] = default(kwargs)
                else:
                    attrs[attribute] = default
        cls.clean(attrs)
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
            data_new[k] = getattr(cls, k).to_python(v)
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

