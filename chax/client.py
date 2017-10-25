import asyncio
import json
import logging

from aiohttp import web

from . import dao
from . import db


class API:
    def __init__(self, db: db.RedisDB, dao: dao.DAO, config):
        self.db = db
        self.dao = dao
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config

    async def register(self, request: web.Request) -> web.Response:
        """
        Обработчик клиенстских запросов на регистрацию.
        """
        data = await request.json()
        try:
            username = data["username"]
            password = data["password"]
            full_name = data["fullName"]
        except KeyError:
            raise web.HTTPBadRequest
        try:
            await self.dao.register(username, password, full_name)
        except dao.UserExistsError:
            return web.json_response({"code": 3,
                                      "note": "User already registered"})
        response = {"code": 0,
                    "note": "Success"}
        return web.json_response(response)

    async def auth(self, request: web.Request) -> web.Response:
        """
        Обработчик клиентских запросов на авторизацию
        """
        data = await request.json()
        try:
            username = data["username"]
            password = data["password"]
        except KeyError:
            raise web.HTTPBadRequest

        try:
            token = await self.dao.auth(username, password)
        except dao.UserNotFoundError:
            return web.json_response({"code": 1,
                                      "note": "User not found"})
        except dao.PasswordError:
            return web.json_response({"code": 2,
                                      "note": "Password is incorrect"})

        response = {"code": 0,
                    "note": "Success",
                    "token": token}

        return web.json_response(response)

    async def ws_handler(self, request: web.Request) -> web.WebSocketResponse:
        """
        Обработчик всех соединений по Web Socket. Подразумевается авторизация абонента по токену
        в первом сообщении.
        """
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        logged_user = None
        try:
            async for msg in ws:
                data = json.loads(msg.data)
                self.logger.debug(data)
                if data["action"] == "login":
                    await self.dao.login(ws, data['username'], data['token'])
                    logged_user = data["username"]
                    request.app['active_users'][logged_user] = ws
                elif logged_user:
                    if data["action"] == "get_user_list":
                        await self.dao.get_user_list(ws)
                    elif data["action"] == "broadcast":
                        await self.dao.send_message(ws, logged_user, data["message"])
                    elif data["action"] == "unicast":
                        await self.dao.send_message(ws, logged_user, data["message"], data["user"])
                else:
                    await ws.send_json({"code": 3,
                                        "note": "User not logged in!"})
                    ws.close()

        except asyncio.CancelledError:
            pass
        finally:
            await ws.close()
            return ws



