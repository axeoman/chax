__version__ = "1.0.0"

import argparse

from aiohttp import web

from chax import client
from chax import config
from chax import db
from chax import tasks
from chax.dao import DAO


def server(host, port, loop=None):
    app = web.Application(loop=loop)
    app['config'] = config
    app['database'] = db.RedisDB(host=config.REDIS_HOST, port=config.REDIS_PORT)
    app['dao'] = DAO(app['database'], config.REDIS_MEMBERS_KEY, config.REDIS_CHANNEL)
    app['api'] = client.API(dao=app['dao'], config=app['config'])
    app.on_startup.append(tasks.start_tasks)
    app.on_cleanup.append(tasks.cleanup_tasks)
    app.router.add_post("/register/", app['api'].register)
    app.router.add_post("/auth/", app['api'].auth)
    app.router.add_get("/ws/", app['api'].ws_handler)
    web.run_app(app,
                host=host,
                port=int(port))


def main():
    parser = argparse.ArgumentParser(description='Simple Web Chat')
    parser.add_argument('--host', type=str, default=config.WEB_HOST, help='IPv4 address')
    parser.add_argument('--port', type=int, default=config.WEB_PORT, help='port')
    args = parser.parse_args()
    print(args)
    server(args.host, args.port)

if __name__ == "__main__":
    main()
