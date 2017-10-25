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
    api = API(config=config, dao=dao)
    return api


@pytest.fixture
def red():
    return redis.StrictRedis(decode_responses=True)


@pytest.fixture
def dao():
    loop = asyncio.get_event_loop()
    db = RedisDB(config, loop=loop)
    return DAO(db=db, config=config)
