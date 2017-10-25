import argparse

from aiohttp import web

from chax import client
from chax import config
from chax import db
from chax import tasks

__version__ = "1.0.0"
__author__ = "Atavin Alexey"


def main(host, port, loop=None):
    app = web.Application(loop=loop)
    database = db.RedisDB(host=config.REDIS_HOST, port=config.REDIS_PORT, config=config)
    api = client.API(db=database, config=config)
    app['api'] = api
    app['config'] = config
    app.on_startup.append(tasks.start_tasks)
    app.on_cleanup.append(tasks.cleanup_tasks)
    app.router.add_post("/register/", api.register)
    app.router.add_post("/auth/", api.auth)
    app.router.add_get("/ws/", api.ws_handler)
    web.run_app(app,
                host=host,
                port=int(port))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simple Web Chat')
    parser.add_argument('host', type=str, default=config.WEB_HOST, help='IPv4 address')
    parser.add_argument('port', type=int, default=config.WEB_PORT, help='port')
    args = parser.parse_args()

    main(args.host, args.port)
