import asyncio
import hashlib
import json
import logging
import os
from base64 import urlsafe_b64encode

import aioredis


class UserNotFoundError(Exception):
    pass


class PasswordError(Exception):
    pass


class UserExistsError(Exception):
    pass


class TokenValidateError(Exception):
    pass


class RedisDB:
    def __init__(self, config, host="0.0.0.0", port=6379, loop=None):
        self.host = host
        self.port = port
        self._pool = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config
        self.loop = loop

    @property
    async def pool(self):
        if not self._pool:
            self._pool = await aioredis.create_pool((self.host, self.port), loop=self.loop)
        return self._pool

    @staticmethod
    def get_hash(password, salt=os.urandom(32)):
        hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100)
        return hash, salt

    async def register(self, username: str, password: str, fullname: str):
        """
        Регистрация пользователя подрузамевает сохранение его личной информации в том числе
        логина и пароля в базу Redis.
        """
        with await (await self.pool) as redis:
            if await redis.exists(username):
                raise UserExistsError
            hash, salt = self.get_hash(password)
            data = {"hash": hash,
                    "salt": salt,
                    "fullname": fullname,
                    "token": ""}

            await redis.hmset_dict(username, data)

    async def auth(self, username: str, password: str) -> str:
        """
        Аунтификация пользователя по данным в Redis.
        """
        with await (await self.pool) as redis:
            hash, salt = await redis.hmget(username, "hash", "salt")
            if not hash:
                raise UserNotFoundError
            new_hash, _ = self.get_hash(password, salt)
            if not new_hash == hash:
                raise PasswordError
            token = self._generate_token()
            await redis.hmset(username, "token", token)
        return token.decode()

    def _generate_token(self) -> str:
        """
        Генерация токена для последующей авторизации в чате.
        """
        return urlsafe_b64encode(os.urandom(32))

    async def check_token(self, username, token):
        """
        Проверка валидности токена.
        """
        with await (await self.pool) as redis:
            db_token = (await redis.hget(username, "token")).decode()
            if token != db_token:
                self.logger.error(f"TokenError! {db_token} != {token}")
                raise TokenValidateError

    async def add_to_chat(self, username: str):
        """
        Добавления пользователя в чат.
        """
        with await (await self.pool) as redis:
            await redis.sadd("chatroom", username)

    async def get_user_list(self) -> list:
        """
        Функция возвращает список всех активных пользователей в чате.
        """
        with await (await self.pool) as redis:
            return await redis.smembers("chatroom", encoding="utf-8")

    async def send_message(self, sender: str, reciever: str, message: str):
        """
        Отправка сообщения в чат. Одна и та же функция обслуживает широковещательные и личные
        сообщения.
        """
        data = {"sender": sender,
                "reciever": reciever,
                "message": message}
        with await (await self.pool) as redis:
            await redis.publish_json("chat", data)

    async def subscribe(self, message_queue: asyncio.Queue):
        """
        Функция осуществляет загрузку всех пришедших сообщения в канале Redis и отправляет для
        обработки в очередь сообщений.
        """
        try:
            with await (await self.pool) as redis:
                ch, *_ = await redis.subscribe('chat')
                async for msg in ch.iter(encoding='utf-8'):
                    data = json.loads(msg)
                    self.logger.debug(msg)
                    await message_queue.put(data)

        except asyncio.CancelledError:
            pass
