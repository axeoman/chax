from . import db
import asyncio


async def start_tasks(app):
    app['chat_reader'] = app.loop.create_task(app['api'].db.subscribe())
    pass


async def cleanup_tasks(app):
    pass
