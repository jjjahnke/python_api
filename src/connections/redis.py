import string
import redis


class RedisClient:
    def __init__(self, host: string, port: int, socket_connect_timeout: float):
        self.host = host
        self.port = port
        self.socket_connect_timeout = socket_connect_timeout
        self.redis_client = redis.Redis(
            host=self.host,
            port=self.port,
            socket_connect_timeout=self.socket_connect_timeout,
        )

    def getRedisClient(self):
        return self.redis_client
