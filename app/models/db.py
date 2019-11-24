from redis import Redis

redis = Redis.from_url(url=f'redis://redis:6379/0')


def search(key: str):
    return redis.scan_iter(match=key)