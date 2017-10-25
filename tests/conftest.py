import asyncio

import pytest
import redis

from chax import config
from chax.client import API
from chax.dao import DAO
from chax.db import RedisDB


@pytest.yield_fixture(scope='function', autouse=True)
def redis_env():
    r = redis.StrictRedis()

    yield

    r.flushall()


@pytest.fixture
def api():
    dao = DAO(db=RedisDB(config), config=config)
    api = API(db=RedisDB(config), config=config, dao=dao)
    return api


@pytest.fixture
def red():
    return redis.StrictRedis(decode_responses=True)


@pytest.fixture
def db():
    loop = asyncio.get_event_loop()
    return RedisDB(config, loop=loop)
