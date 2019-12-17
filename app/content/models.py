from datetime import datetime
import json
from time import time
from typing import Dict
from uuid import uuid4

from models.basemodel import BaseModel
from models.basemodel import TextField, DateField
from models.db import db
from models.exceptions import NotFound, ValidationError


class RecentPosts:
    max_posts = 10

    def __init__(self):
        self.idx = 1
        self.posts = []
        for post in db.search("blogpost:*"):
            post = json.loads(post)
            self.posts.append(post['id'])
            self.idx += 1
            if self.idx == self.max_posts:
                break

    def add(self, id: str) -> None:
        self.posts = [id] + self.posts
        if self.idx > self.max_posts:
            del self.posts[-1]
            self.idx -= 1


recent_posts = RecentPosts()


class BlogPost(BaseModel):
    id = TextField(default=lambda kwargs: BlogPost._generate_id(**kwargs))
    title = TextField(default='')
    content = TextField(default='')
    author = TextField(default='')
    author_id = TextField(default='')

    @classmethod
    def create(cls, **kwargs):
        instance = super().create(**kwargs)
        recent_posts.add(instance.id)
        return instance

    @staticmethod
    def _generate_id(**kwargs):
        return f'blogpost:{str(uuid4())[:8]}:{kwargs["author"]}'

    @staticmethod
    def validate(data: Dict):
        if 'author' not in data:
            raise ValidationError

    @staticmethod
    def info_to_db_key(**kwargs) -> str:
        return f'blogpost:*:{kwargs["author"]}' if 'author' in kwargs else 'blogpost:*'

    def __str__(self):
        return f'Blogpost:\n \t id: {self.id}\n \t author: {self.author}\n' + \
               f'\t title: {self.title}\n \t content: {self.content}'


class Likes(BaseModel):
    id = TextField(default='')
    blogpost_id = TextField(default='')
    user_id = TextField(default='')
    date = DateField(default=lambda _: datetime.now())

    @staticmethod
    def validate(data: Dict):
        return 'id' in data and 'user_id' in data and 'blogpost_id' in data

    @staticmethod
    def _generate_id(**kwargs):
        return f'like:{kwargs["user_id"]}:{kwargs["blogpost_id"]}'


    @staticmethod
    def info_to_db_key(**kwargs) -> str:
        return f'like:{kwargs["user_id"]}:{kwargs["blogpost_id"]}'




