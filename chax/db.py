import asyncio
import json
import logging

import aioredis


class RedisDB:
    def __init__(self, host="0.0.0.0", port=6379, loop=None):
        self.host = host
        self.port = port
        self._pool = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.loop = loop

    @property
    def pool(self):
        if not self._pool:
            raise Exception("Create redis pool with create_pool() first!")
        return self._pool

    async def create_pool(self):
        self._pool = await aioredis.create_pool((self.host, self.port), loop=self.loop)

    async def check_exists(self, username):
        with await self.pool as redis:
            return await redis.exists(username)

    async def add_user_data(self, username, data):
        with await self.pool as redis:
            await redis.hmset_dict(username, data)

    async def get_user_data(self, username):
        with await self.pool as redis:
            return await redis.hgetall(username)

    async def save_token(self, username, token):
        with await self.pool as redis:
            return await redis.hset(username, "token", token)

    async def get_token(self, username):
        with await self.pool as redis:
            return (await redis.hget(username, "token")).decode()

    async def add_member(self, username: str, set_key: str):
        """
        Добавления пользователя в чат.
        """
        with await self.pool as redis:
            await redis.sadd(set_key, username)

    async def get_members(self, set_key: str) -> list:
        """
        Функция возвращает список всех активных пользователей в чате.
        """
        with await self.pool as redis:
            return await redis.smembers(set_key, encoding="utf-8")

    async def publish_message(self, channel, data):
        """
        Публикация сообщения в канал Redis.
        """
        with await self.pool as redis:
            await redis.publish_json(channel, data)

    async def subscribe(self, message_queue: asyncio.Queue, channel: str):
        """
        Функция осуществляет загрузку всех пришедших сообщения в канале Redis и отправляет для
        обработки в очередь сообщений.
        """
        with await self.pool as redis:
            ch, *_ = await redis.subscribe(channel)
            async for msg in ch.iter(encoding='utf-8'):
                data = json.loads(msg)
                self.logger.debug(msg)
                await message_queue.put(data)
