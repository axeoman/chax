import pytest
from aiohttp import web
import redis
import asyncio

from chax.client import API
from chax import db
from chax import config
from tests.test_db import red
import json

NAME = "axeo"
PASSWORD = "12345678"
FULLNAME = "Atavin Alexey"


@pytest.fixture
def api():
    api = API(db=db.RedisDB(config), config=config)
    return api

async def test_register(test_client, loop, red, api):

    app = web.Application()
    app.router.add_post('/register/', api.register)
    app.router.add_post('/auth/', api.auth)
    data = {
            "username" : NAME,
            "password" : PASSWORD,
            "fullName": FULLNAME,
            }
    client = await test_client(app)
    resp = await client.post('/register/', data=json.dumps(data))
    assert resp.status == 200

    redis_data = red.hgetall(NAME)
    assert redis_data["fullname"] == FULLNAME


