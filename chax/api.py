from aiohttp import web
from . import db


class API:

    def __init__(self, db: db.RedisDB):
        self.db = db
        pass

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