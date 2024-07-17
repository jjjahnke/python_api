from fastapi import FastAPI
from connections.redis import RedisClient
from middleware.global_timeout import GlobalTimeoutMiddleware
from model.cd_model import User, UserResponse
from model.nested import NestedModel


class PythonAPIApp:
    def __init__(
        self,
        app: FastAPI = FastAPI(),
        redis: RedisClient = RedisClient("redis", 6379, 10).getRedisClient(),
    ):
        self.app = app
        self.redis = redis

    def getRedisClient(self):
        return self.redis

    def getFastAPIApp(self):
        return self.app


papp = PythonAPIApp(
    app=FastAPI(), redis=RedisClient("redis", 6379, 10).getRedisClient()
)

papp.app.add_middleware(GlobalTimeoutMiddleware, timeout=10)


@papp.app.get("/")
async def root():
    return {"message": "Hello bogus"}


@papp.app.get("/count")
async def count():
    r = papp.getRedisClient()
    return {"count": r.incr("count")}


@papp.app.post("/nested")
async def post_nested(nested: NestedModel) -> NestedModel:
    return nested


@papp.app.get("/nested")
async def get_nested() -> NestedModel:
    return NestedModel(
        test=[
            NestedModel.TestModel(name="foo", age=1, enum="foo"),
            NestedModel.TestModel(name="bar", age=2, enum="bar"),
        ]
    )


users = {}

for i in range(10):
    tmpUser = User(username=f"user_{i}", email=f"email_{i}")
    users[str(tmpUser.uuid)] = tmpUser


@papp.app.get("/user/{user_id}")
async def read_user(user_id: str) -> UserResponse:
    return users[user_id]


@papp.app.get("/users")
async def read_users() -> list[UserResponse]:
    return [UserResponse.newResponse(user) for user in users.values()]


@papp.app.post("/user")
async def create_user(user: UserResponse) -> User:
    users[user.uuid] = user
    return user
