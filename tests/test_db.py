import pytest
import redis
from chax.db import *
import pytest_asyncio
from chax import config

NAME = "axeo"
PASSWORD = "12345678"
FULLNAME = "Atavin Alexey"

pytestmark = pytest.mark.asyncio


@pytest.yield_fixture(scope='function', autouse=True)
def redis_env():
    r = redis.StrictRedis()

    yield

    r.flushall()


@pytest.fixture
def db():
    return RedisDB(config)


@pytest.fixture
def red():
    return redis.StrictRedis(decode_responses=True)


async def test_register(event_loop, db, red):

    await db.register(NAME, PASSWORD, FULLNAME)
    data = red.hgetall(NAME)
    assert data['fullname'] == FULLNAME

async def test_auth(event_loop, db, red):

    await db.register(NAME, PASSWORD, FULLNAME)
    token = await db.auth(NAME, PASSWORD)
    data = red.hgetall(NAME)
    assert token.decode() == data['token']

async def test_wrong_pass(event_loop, db):
    await db.register(NAME, PASSWORD, FULLNAME)
    with pytest.raises(PasswordError):
        await db.auth(NAME, "WrongPassword")

async def test_double_registration(event_loop, db):
    await db.register(NAME, PASSWORD, FULLNAME)
    with pytest.raises(UserExistsError):
        await db.register(NAME, PASSWORD, FULLNAME)


async def test_user_not_found(event_loop, db):
    with pytest.raises(UserNotFoundError):
         await db.auth("WrongName", "WrongPassword")




