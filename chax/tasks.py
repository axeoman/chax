import asyncio
import logging


logger = logging.getLogger(__file__)

async def message_handler(app, queue):
    """
    Сопрограмма обеспечивающая чтение сообщения в очереди и реакцию на него. Будь то сообщение
    направлено конкретному пользователю, или же широковещательное сообщение.
    Обработчиков может быть запущенно несколько.
    """
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

    except asyncio.CancelledError:
        pass

async def start_tasks(app):
    queue = app['message_queue'] = asyncio.Queue()
    app['chat_reader'] = app.loop.create_task(app['api'].db.subscribe(queue))
    app['message_handlers'] = list()
    for _ in range(app['config'].MESSAGE_HANDLERS):
        app['message_handlers'].append(app.loop.create_task(message_handler(app, queue)))


async def cleanup_tasks(app):
    for handler in app['message_handlers']:
        handler.cancel()
    app['chat_reader'].cancel()
