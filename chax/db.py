import asyncio
import aioredis
import hashlib
import os
from base64 import standard_b64encode
import logging
import json

class UserNotFoundError(Exception):
    pass


class PasswordError(Exception):
    pass


class UserExistsError(Exception):
    pass


class TokenValidateError(Exception):
    pass


class RedisDB:

    def __init__(self, host="0.0.0.0", port=6379):
        self.host = host
        self.port = port
        self._pool = None
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    async def pool(self):
        if not self._pool:
            self._pool = await aioredis.create_pool((self.host, self.port))
        return self._pool

    @staticmethod
    def get_hash(password, salt=os.urandom(32)):
        hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100)
        return hash, salt

    async def register(self, username: str, password: str, fullname: str):
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
        with await (await self.pool) as redis:
            hash, salt = await redis.hmget(username, "hash", "salt")
            if not hash:
                raise UserNotFoundError
            new_hash, _ = self.get_hash(password, salt)
            if not new_hash == hash:
                raise PasswordError
            token = self._generate_token()
            await redis.hmset(username, "token", token)
        return token

    def _generate_token(self) -> str:
        return standard_b64encode(os.urandom(32))

    async def check_token(self, username, token):
        with await (await self.pool) as redis:
            db_token = await redis.hget(username, "token")
            if token != db_token:
                raise TokenValidateError

    async def add_to_chat(self, username):
        with await (await self.pool) as redis:
            await redis.sadd("chatroom", username)

    async def get_user_list(self) -> list:
        with await (await self.pool) as redis:
            return await redis.smembers("chatroom", encoding="utf-8")

    async def send_message(self, sender, reciever, message):
        data = {"sender": sender,
                "reciever": reciever,
                "message": message}
        with await (await self.pool) as redis:
            await redis.publish_json("chat", data)

    async def subscribe(self, message_queue: asyncio.Queue):
        with await (await self.pool) as redis:
            try:
                ch, *_ = await redis.subscribe('chat')
                async for msg in ch.iter(encoding='utf-8'):
                    data = json.loads(msg)
                    await message_queue.put(data)

            except asyncio.CancelledError():
                pass

