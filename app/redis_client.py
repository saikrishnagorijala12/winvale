import redis

from app.config import settings

redis_kwargs = {
    "host": settings.REDIS_HOST,
    "port": settings.REDIS_PORT,
    "decode_responses": settings.REDIS_DECODE_RESPONSES,
    "socket_connect_timeout": settings.REDIS_SOCKET_CONNECT_TIMEOUT,
    "socket_timeout": settings.REDIS_SOCKET_TIMEOUT,
    "ssl": settings.REDIS_SSL,
}

if settings.REDIS_SSL:
    redis_kwargs["ssl_cert_reqs"] = None

redis_client = redis.Redis(**redis_kwargs)
