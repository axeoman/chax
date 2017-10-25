import asyncio
import json
import logging
from multiprocessing import Process

import pytest
import websockets
from aiohttp import ClientSession

import chax

"""
Этот тест следуюет запускать с параметром -p no:aiohttp

1. Зарегистрировать трех пользователей
2. Произвести аунтификацию всех трёх
3. Послать сообщение броадкастом от первого - проверить у остальных двух
4. Послать сообщение от второго третьему - убедиться что сообщение дошло к третьему, но не пришло 
первому.
"""


@pytest.yield_fixture(scope='function', autouse=True)
def server():
    process = Process(target=chax.main, args=("0.0.0.0", 8888))
    process.start()
    yield

    process.terminate()


reg_data_one = {
    "username": "Vasya1",
    "password": "VasinPass1",
    "fullName": "Vasiliy One Pupkin",
}

reg_data_two = {
    "username": "Vasya2",
    "password": "VasinPass2",
    "fullName": "Vasiliy Two Pupkin",
}

reg_data_three = {
    "username": "Vasya3",
    "password": "VasinPass3",
    "fullName": "Vasiliy Three Pupkin",
}

HTTP_SOCKET = "http://0.0.0.0:8888"
WS = "ws://127.0.0.1:8888/ws/"


async def register_and_auth(data, red):
    async with ClientSession() as session:
        async with session.post(f'{HTTP_SOCKET}/register/', data=json.dumps(data)) as resp:
            assert resp.status == 200

    redis_data = red.hgetall(data["username"])
    assert redis_data["fullname"] == data["fullName"]

    async with ClientSession() as session:
        async with session.post(f'{HTTP_SOCKET}/auth/', data=json.dumps(data)) as resp:
            assert resp.status == 200
            response_data = await resp.json()

    assert response_data['code'] == 0
    redis_data = red.hgetall(data["username"])
    assert redis_data['token'] == response_data['token']
    return response_data['token']


async def one(token):
    logger = logging.getLogger("One")
    async with websockets.connect(WS) as websocket:
        login = {
            "action": "login",
            "username": reg_data_one["username"],
            "token": token
        }
        await websocket.send(json.dumps(login))

        assert {"code": 0, "note": "Success"} == json.loads(await websocket.recv())

        logger.debug("Sending Broadcast!")
        await websocket.send(json.dumps({
            "action": "broadcast",
            "message": "Hi All"
        }
        ))
        assert {"code": 0, "note": "Success"} == json.loads(await websocket.recv())


async def two(token):
    logger = logging.getLogger("Two")

    async with websockets.connect(WS) as websocket:
        login = {
            "action": "login",
            "username": reg_data_two["username"],
            "token": token
        }
        await websocket.send(json.dumps(login))

        assert {"code": 0, "note": "Success"} == json.loads(await websocket.recv())

        broadcast_msg = await websocket.recv()
        logger.critical("Broadcast Message Recieved!")
        assert {"sender": "Vasya1", "reciever": None, "message": "Hi All"} == \
               json.loads(broadcast_msg)
        logger.debug("Sending Unicast!")

        await websocket.send(json.dumps(
            {
                "action": "unicast",
                "user": "Vasya3",
                "message": "Hi Vasiliy!"
            }
        ))
        assert {"code": 0, "note": "Success"} == json.loads(await websocket.recv())


async def three(token):
    logger = logging.getLogger("Three")
    async with websockets.connect(WS) as websocket:
        login = {
            "action": "login",
            "username": reg_data_three["username"],
            "token": token
        }
        await websocket.send(json.dumps(login))

        assert {"code": 0, "note": "Success"} == json.loads(await websocket.recv())
        assert {"sender": "Vasya1", "reciever": None, "message": "Hi All"} == \
               json.loads(await websocket.recv())

        unicast_message = await websocket.recv()
        logger.critical("Unicast message Recieved!")
        assert {"sender": "Vasya2", "reciever": "Vasya3", "message": "Hi Vasiliy!"} == \
               json.loads(unicast_message)


@pytest.mark.asyncio
async def test_chat(red, event_loop):
    token_one = await register_and_auth(reg_data_one, red)
    token_two = await register_and_auth(reg_data_two, red)
    token_three = await register_and_auth(reg_data_three, red)
    # await asyncio.sleep(2)
    tasks = [one(token_one), two(token_two), three(token_three)]

    await asyncio.gather(*tasks)
