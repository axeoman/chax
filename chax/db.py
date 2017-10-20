import aioodbc
import asyncio
import aioredis
import hashlib
import os
from base64 import standard_b64encode

class UserNotFoundError(Exception):
    pass


class PasswordError(Exception):
    pass


class UserExistsError(Exception):
    pass


class RedisDB:

    def __init__(self, host="0.0.0.0", port=6379):
        self.host = host
        self.port = port
        self._pool = None

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
            new_hash, _ = self.get_hash(password, salt)
            if not new_hash == hash:
                raise PasswordError

            token = self._generate_token()
            await redis.hmset(username, "token", token)

        return token

    def _generate_token(self) -> str:
        return standard_b64encode(os.urandom(32))



