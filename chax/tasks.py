from . import db
import asyncio
import logging


logger = logging.getLogger(__file__)

async def message_handler(app, queue):

    try:
        while True:
            msg = await queue.get()
            logger.debug(msg)
            reciever = msg['reciever']
            if reciever is None:
                tasks = [ws.send_json(msg) for username, ws in app['active_users'].items()]
                results = await asyncio.gather(*tasks, return_exceptions=False)
            else:
                try:
                    ws = app['active_users'][reciever]
                    await ws.send_json(msg)
                except KeyError:
                    pass

    except asyncio.CancelledError():
        pass

async def start_tasks(app):
    queue = app['message_queue'] = asyncio.Queue()
    app['chat_reader'] = app.loop.create_task(app['api'].db.subscribe(queue))
    app['message_handler'] = app.loop.create_task(message_handler(app, queue))


async def cleanup_tasks(app):
    pass

