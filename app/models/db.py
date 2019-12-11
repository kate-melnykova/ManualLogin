import json

from redis import Redis, exceptions

# redis = Redis.from_url(url=f'redis://redis:6379/0')

# def search(key: str):
#     return redis.scan_iter(match=key)


class DBmetaclass(type):
    def __init__(cls, *args, **kwargs):
        cls._redis = Redis.from_url(url=f'redis://redis:6379/0')

    @property
    def redis(cls) -> 'Redis':
        try:
            cls._redis.ping()
        except exceptions.ConnectionError:
            cls._redis = Redis.from_url(url=f'redis://redis:6379/0')
        except exceptions.BusyLoadingError:
            return Redis.from_url(url=f'redis://redis:6379/0')

        return cls._redis


class DB(metaclass=DBmetaclass):
    @classmethod
    def load(cls, key: str) -> str or None:
        """
        loads the value stored under given key
        :param db_id:
        :return: the corresponding value or, if key is not found, None
        """
        return cls.redis.get(key)

    @classmethod
    def search(cls, pattern: str) -> 'iter':
        """
        Find all keys that match given regex pattern
        :param pattern: the regex pattern for db keys
        :return: iterator over values that match the given pattern
        """
        keys = cls.redis.scan_iter(match=pattern)
        for key in keys:
            yield json.loads(cls.redis.get(key))

    @classmethod
    def exists(cls, key: int or str) -> bool:
        """
        Verifies if the exists given key in the db
        :param key: the potential key of the db
        :return: true if the key is in db, false otherwise
        """
        return bool(cls.redis.exists(key))

    @classmethod
    def save(cls, key: str, value: str) -> None:
        """
        Add/update db record for given (key, value) pair
        :param key: the key in the db
        :param value: the value to be stored under the given key in db
        """
        cls.redis.set(key, value)

    @classmethod
    def delete(cls, key: str) -> None:
        """
        Remove the (key, value) pair from the db
        :param key: the key in the db
        """
        cls.redis.delete(key)