from fastapi import FastAPI
from connections.redis import RedisClient
from middleware.global_timeout import GlobalTimeoutMiddleware


class PythonAPIApp:
    def __init__(
        self,
        app: FastAPI = FastAPI(),
        redis: RedisClient = RedisClient("redis", 6379, 10).getRedisClient(),
    ):
        self.fastapi_app = app
        self.redis_client = redis

    def getRedisClient(self):
        return self.redis_client

    def getFastAPIApp(self):
        return self.fastapi_app


papp = PythonAPIApp()
app = papp.fastapi_app()

app.add_middleware(GlobalTimeoutMiddleware, timeout=10)


@app.get("/")
async def root():
    return {"message": "Hello bogus"}


@app.get("/count")
async def count():
    r = papp.getRedisClient()
    return {"count": r.incr("count")}
