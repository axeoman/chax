from aiohttp import web
from . import db
import json
import asyncio
import logging
import traceback

class API:

    def __init__(self, db: db.RedisDB):
        self.db = db
        self.logger = logging.getLogger(self.__class__.__name__)

    async def register(self, request: web.Request) -> web.Response:
        data = await request.json()
        try:
            username = data["username"]
            password = data["password"]
            full_name = data["fullName"]
        except KeyError:
            raise web.HTTPBadRequest
        try:
            await self.db.register(username, password, full_name)
        except db.UserExistsError:
            return web.json_response({"code": 3,
                                      "note": "User already registered"})
        response = {"code": 0,
                    "note": "Success"}
        return web.json_response(response)

    async def auth(self, request: web.Request) -> web.Response:
        data = await request.json()
        try:
            username = data["username"]
            password = data["password"]
        except KeyError:
            raise web.HTTPBadRequest

        try:
            token = await self.db.auth(username, password)
        except db.UserNotFoundError:
            return web.json_response({"code": 1,
                                      "note": "User not found"})
        except db.PasswordError:
            return web.json_response({"code": 2,
                                      "note": "Password is incorrect"})

        response = {"code": 0,
                    "note": "Succcess",
                    "token": token}

        return web.json_response(response)

    async def ws_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        logged_user = None
        try:
            async for msg in ws:
                data = json.loads(msg.data)
                if data["action"] == "login":
                    self._login(ws, data['username'], data['token'])
                    logged_user = data["username"]
                elif logged_user:
                    if data["action"] == "get_user_list":
                        self._get_user_list(ws)
                    elif data["action"] == "broadcast":
                        self._send_broadcast(ws, data["message"])
                    elif data["action"] == "unicast":
                        self._send_unicast(ws, logged_user, data["user"], data["message"])
                else:
                    await ws.send_json({"code": 3,
                                        "note": "User not logged in!"})
                    ws.close()

        except asyncio.CancelledError:
            pass

        finally:
            await ws.close()
            return ws

    async def _login(self, ws, username, token):
        try:
            await self.db.check_token(username, token)
        except db.TokenValidateError:
            await ws.send_json({"code": 1,
                                "note": "Invalid username/token pair"})
            ws.close()
        try:
            await self.db.add_to_chat(username)
            await ws.send_json({"code": 0,
                                "note": "Success"})
        except Exception as e:
            self.logger.error(traceback.format_exc())
            await ws.send_json({"code": 2,
                                "note": "Failed to login"})

    async def _get_user_list(self, ws):
        await ws.send_json({"users": await self.db.get_user_list()})

    async def _send_broadcast(self, ws, message):
        await self.db.broadcast(message)
        await ws.send_json({"code": 0,
                            "note": "Success"})

    async def _send_unicast(self, ws, sender, reciever, message):
        await self.db.unicast(sender, reciever, message)
        await ws.send_json({"code": 0,
                            "note": "Success"})

