import json
from typing import List
from uuid import uuid4

from models.db import redis as r
from models.basemodel import NotFound


class PostNotFound(NotFound):
    message = 'Blogpost is not found. Maybe, try another id?'


class BlogPost:
    _attributes = ['title', 'author', 'content']

    @staticmethod
    def _generate_id():
        return f'blogpost:{uuid4()[:8]}'

    def __init__(self, title: str, author: str, content: str, id=None):
        self.title = title
        self.author = author
        self.content = content
        self.id = id or self._generate_id()

    @classmethod
    def create(cls, title: str, author: str, content: str):
        post = cls(title, author, content)
        post.save()
        return post

    def save(self):
        d = dict()
        for attribute in self._attributes:
            d[attribute] = self.__getattribute__(attribute)
        r.set(id, json.dumps(d))

    @classmethod
    def load(cls, id: str):
        data = r.get(id)
        if data is None:
            raise PostNotFound
        return cls(**json.loads(data))
