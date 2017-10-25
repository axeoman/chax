import asyncio
import hashlib
import logging
import os
import traceback
from base64 import urlsafe_b64encode

from aiohttp import web

from chax import db


class UserExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class PasswordError(Exception):
    pass


class DAO:
    def __init__(self, db: db.RedisDB, config):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.db = db
        self.config = config

    def get_hash(self, password, salt=os.urandom(32)):
        h = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100)
        return h, salt

    @staticmethod
    def generate_token() -> str:
        """
        Генерация токена для последующей авторизации в чате.
        """
        return urlsafe_b64encode(os.urandom(32)).decode()

    async def register(self, username: str, password: str, full_name: str):
        """
         Регистрация пользователя подрузамевает сохранение его личной информации в том числе
         логина и пароля в базу Redis.
         """
        if await self.db.check_exists(username):
            raise UserExistsError
        else:
            h, salt = self.get_hash(password)
            data = {"hash": h,
                    "salt": salt,
                    "fullname": full_name,
                    "token": ""}
            await self.db.add_user_data(username, data)

    async def auth(self, username: str, password: str) -> str:
        """
        Аунтификация пользователя по данным в Redis.
        """
        if not await self.db.check_exists(username):
            raise UserNotFoundError

        db_data = await self.db.get_user_data(username)
        new_hash, _ = self.get_hash(password, salt=db_data[b'salt'])

        if not new_hash == db_data[b'hash']:
            raise PasswordError

        token = self.generate_token()
        await self.db.save_token(username, token)

        return token

    async def login(self, ws: web.WebSocketResponse, username: str, token: str):
        """
        Функция авторизации пользователя с валидацией его токена.
        """
        try:
            if await self.check_token(username, token):
                await self.db.add_member(username, self.config.REDIS_MEMBERS_KEY)
                await ws.send_json({"code": 0,
                                    "note": "Success"})
            else:
                await ws.send_json({"code": 1,
                                    "note": "Invalid username/token pair"})
                ws.close()
        except Exception as e:
            self.logger.error(traceback.format_exc())
            await ws.send_json({"code": 2,
                                "note": "Failed to login"})

    async def check_token(self, username, token):
        db_token = await self.db.get_token(username)
        if token != db_token:
            self.logger.error(f"TokenError! {db_token} != {token}")
            return False
        else:
            return True

    async def get_user_list(self, ws: web.WebSocketResponse):
        """
        Получение списка активных пользователей.
        """
        await ws.send_json({"users": await self.db.get_members(self.config.REDIS_MEMBERS_KEY)})

    async def send_message(self, ws: web.WebSocketResponse, sender: str, message: str,
                           reciever: str = None):
        """
        Отправка сообщений конкретному пользователю или широковещательно.
        """
        data = {"sender": sender,
                "reciever": reciever,
                "message": message}
        await self.db.publish_message(self.config.REDIS_CHANNEL, data)
        await ws.send_json({"code": 0,
                            "note": "Success"})

    async def subscribe(self, message_queue: asyncio.Queue):
        try:
            await self.db.subscribe(message_queue, self.config.REDIS_CHANNEL)
        except asyncio.CancelledError:
            pass
