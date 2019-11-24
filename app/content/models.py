from typing import Dict
from uuid import uuid4

from models.db import redis
from models.basemodel import BaseModel, ValidationError
from models.basemodel import IdField, TextField, UserField


class BlogPost(BaseModel):
    id = IdField()
    title = TextField(default='')
    content = TextField(default='')
    author = UserField(default='')
    author_id = IdField(default='')


    @staticmethod
    def validate(data: Dict):
        if 'author' not in data:
            raise ValidationError

    @staticmethod
    def _generate_id(**kwargs):
        return f'blogpost:{str(uuid4())[:8]}:{kwargs["author"]}'

    @classmethod
    def defaults(cls, **kwargs):
        return {
            'id': cls._generate_id(id=kwargs.get('id'), author=kwargs.get('author')),
            'author': cls.author.default,
            'author_id': cls.author_id.default,
            'title': cls.title.default,
            'content': cls.content.default,
        }

    @classmethod
    def get_attributes(cls):
        return list(cls.defaults().keys())

    @staticmethod
    def info_to_db_key(**kwargs) -> str:
        return f'blogpost:*:{kwargs["author"]}' if 'author' in kwargs else 'blogpost:*'


class RecentPosts:
    max_posts = 10

    def __init__(self):
        idx = 1
        self.post_ids = []
        for key in redis.scan_iter(match="blogpost:*"):
            self.post_ids.append(key)
            idx += 1
            if idx > 10:
                break

    def add(self, id: str) -> None:
        self.post_ids = [id] + self.post_ids
        if len(self.post_ids) > self.max_posts:
            del self.post_ids[-1]



