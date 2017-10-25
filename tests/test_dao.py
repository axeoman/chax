import pytest

from chax.dao import *

NAME = "axeo"
PASSWORD = "12345678"
FULLNAME = "Atavin Alexey"

pytestmark = pytest.mark.asyncio


# Эти тесты следуюет запускать с параметром -p no:aiohttp"


async def test_register(event_loop, dao, red):
    await dao.register(NAME, PASSWORD, FULLNAME)
    data = red.hgetall(NAME)
    assert data['fullname'] == FULLNAME


async def test_auth(event_loop, dao, red):
    await dao.register(NAME, PASSWORD, FULLNAME)
    token = await dao.auth(NAME, PASSWORD)
    data = red.hgetall(NAME)
    assert token == data['token']


async def test_wrong_pass(event_loop, dao):
    await dao.register(NAME, PASSWORD, FULLNAME)
    with pytest.raises(PasswordError):
        await dao.auth(NAME, "WrongPassword")


async def test_double_registration(event_loop, dao):
    await dao.register(NAME, PASSWORD, FULLNAME)
    with pytest.raises(UserExistsError):
        await dao.register(NAME, PASSWORD, FULLNAME)


async def test_user_not_found(event_loop, dao):
    with pytest.raises(UserNotFoundError):
        await dao.auth("WrongName", "WrongPassword")
