from redis import Redis

redis = Redis.from_url(url=f'redis://redis:6379/0')