import json
from uuid import uuid4

import redis


r = redis.Redis.from_url(url=f'redis://redis:6379/0')


class PostNotFound(Exception):
    pass


class BlogPost:
    @staticmethod
    def _generate_id():
        return f'blogpost:{uuid4()}'

    def __init__(self, title, author, content, id=None):
        self.title = title
        self.author = author
        self.content = content
        self.id = id or self._generate_id()

    @classmethod
    def create(cls, title, author, content):
        post = cls(title, author, content)
        post.save()
        return post

    def save(self):
        d = dict()
        d['id'] = self.id
        d['title'] = self.title
        d['author'] = self.author
        d['content'] = self.content
        r.set(id, json.dumps(d))

    @classmethod
    def load(cls, id):
        data = r.get(id)
        if data is None:
            raise PostNotFound
        return cls(**json.loads(data))
