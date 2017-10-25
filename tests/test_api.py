import json

from aiohttp import web

NAME = "axeo"
PASSWORD = "12345678"
FULLNAME = "Atavin Alexey"

data = {
    "username": NAME,
    "password": PASSWORD,
    "fullName": FULLNAME,
}


async def register(api, loop, test_client, red):
    app = web.Application()
    app.router.add_post('/register/', api.register)
    app.router.add_post('/auth/', api.auth)
    await api.dao.db.create_pool()
    client = await test_client(app)
    resp = await client.post('/register/', data=json.dumps(data))
    assert resp.status == 200
    redis_data = red.hgetall(NAME)
    assert redis_data["fullname"] == FULLNAME

    return app


async def test_register(test_client, loop, red, api):
    app = await register(api, loop, test_client, red)


async def test_bad_auth(test_client, loop, red, api):
    app = await register(api, loop, test_client, red)
    data = {
        "username": "BadUser",
        "password": PASSWORD,
            }
    client = await test_client(app)
    resp = await client.post('/auth/', data=json.dumps(data))
    assert resp.status == 200
    assert {'code': 1, 'note': 'User not found'} == await resp.json()


async def test_auth(test_client, loop, red, api):
    app = await register(api, loop, test_client, red)
    client = await test_client(app)
    resp = await client.post('/auth/', data=json.dumps(data))
    assert resp.status == 200
    response_data = await resp.json()
    assert response_data['code'] == 0
    redis_data = red.hgetall(NAME)
    assert redis_data['token'] == response_data['token']


async def test_bad_password(test_client, loop, red, api):
    app = await register(api, loop, test_client, red)
    data = {
        "username": NAME,
        "password": "B@dpaSSw0rd",
        "fullName": FULLNAME,
    }
    client = await test_client(app)
    resp = await client.post('/auth/', data=json.dumps(data))
    assert resp.status == 200
    assert {"code": 2, "note": "Password is incorrect"} == await resp.json()
