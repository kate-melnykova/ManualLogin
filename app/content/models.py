from typing import Dict
from uuid import uuid4

from models.basemodel import BaseModel, ValidationError


class BlogPost(BaseModel):
    _attributes = ['title', 'author', 'content', 'id']

    @staticmethod
    def _generate_id(**kwargs):
        return f'blogpost:{uuid4()[:8]}'

    @staticmethod
    def validate(data: Dict):
        if 'author' not in data:
            raise ValidationError

    @classmethod
    def defaults(cls, **kwargs):
        return {
            'id': cls._generate_id(),
            'title': '',
            'content': '',
        }

