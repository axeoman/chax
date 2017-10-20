import pytest
import redis
from chax.db import RedisDB
import pytest_asyncio


NAME = "axeo"
PASSWORD = "12345678"
FULLNAME = "Atavin Alexey"

pytestmark = pytest.mark.asyncio


@pytest.yield_fixture(scope='session', autouse=True)
def redis_env():
    r = redis.StrictRedis()

    yield

    r.flushall()

async def test_register(event_loop):

    db = RedisDB()
    await db.register(NAME, PASSWORD, FULLNAME)
    r = redis.StrictRedis()
    data = r.hgetall(NAME)
    assert data[b'fullname'] == FULLNAME.encode()

async def test_auth(event_loop):

    db = RedisDB()
    await db.register(NAME, PASSWORD, FULLNAME)
    token = await db.auth(NAME, PASSWORD)
    r = redis.StrictRedis()
    data = r.hgetall(NAME)
    assert token == data[b'token']

