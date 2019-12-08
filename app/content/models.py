from time import time
from typing import Dict
from uuid import uuid4

from models.basemodel import BaseModel
from models.basemodel import TextField, DateField
from models.exceptions import NotFound, ValidationError


class BlogPost(BaseModel):
    id = TextField()
    title = TextField(default='')
    content = TextField(default='')
    author = TextField(default='')
    author_id = TextField(default='')
    date = DateField(default=int(time()))

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
            'id': cls._generate_id(author=kwargs.get('author')),
            'author': cls.author.default,
            'author_id': cls.author_id.default,
            'title': cls.title.default,
            'content': cls.content.default,
            'date': cls.date.default
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
        r = BlogPost.get_connection()
        for key in r.scan_iter(match="blogpost:*"):
            self.post_ids.append(key)
            idx += 1
            if idx > 10:
                break

    def add(self, id: str) -> None:
        self.post_ids = [id] + self.post_ids
        if len(self.post_ids) > self.max_posts:
            del self.post_ids[-1]


class Likes(BaseModel):
    id = TextField(default='')
    blogpost_id = TextField(default='')
    user_id = TextField(default='')

    @staticmethod
    def validate(data: Dict):
        r = Likes.get_connection()
        return 'id' in data and 'user_id' in data and 'blogpost_id' in data

    @staticmethod
    def _generate_id(**kwargs):
        return f'like:{kwargs["user_id"]}:{kwargs["blogpost_id"]}'

    @classmethod
    def defaults(cls, **kwargs):
        return {
            'id': cls._generate_id(user_id=kwargs.get('user_id'), blogpost_id=kwargs.get('blogpost_id')),
            'blogpost_id': cls.blogpost_id.default,
            'user_id': cls.user_id.default
        }

    @classmethod
    def get_attributes(cls):
        return list(cls.defaults().keys())

    @staticmethod
    def info_to_db_key(**kwargs) -> str:
        return f'like:{kwargs["user_id"]}:{kwargs["blogpost_id"]}'




