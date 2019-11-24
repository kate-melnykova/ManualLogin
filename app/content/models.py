from typing import Dict
from uuid import uuid4

from models.basemodel import BaseModel, ValidationError


class BlogPost(BaseModel):
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
            'author_id': '',
            'title': '',
            'content': '',
        }

    @classmethod
    def get_attributes(cls):
        return list(cls.defaults().keys()) + ['author']

    @staticmethod
    def info_to_db_key(**kwargs) -> str:
        return f'blogpost:*:{kwargs["author"]}' if 'author' in kwargs else 'blogpost:*'


class RecentPosts:
    max_posts = 10

    def __init__(self):
        self.post_ids = []

    def add(self, id: str) -> None:
        self.post_ids = [id] + self.post_ids
        if len(self.post_ids) > self.max_posts:
            del self.post_ids[-1]



