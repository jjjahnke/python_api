import pytest
from fastapi.testclient import TestClient
from connections.redis import RedisClient
from app import papp as app

@pytest.fixture
def redisdb():
    app.redis = RedisClient("localhost", 6379, 1).getRedisClient()

@pytest.fixture
def client():
    return TestClient(app.getFastAPIApp())

def test_root(client, redisdb):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello bogus"}

def test_count(client, redisdb):
    response = client.get("/count")
    assert response.status_code == 200
    assert response.json() == {"count": 1}  
    response = client.get("/count")
    assert response.status_code == 200
    assert response.json() == {"count": 2}
