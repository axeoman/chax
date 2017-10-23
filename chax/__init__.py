import argparse
import sys
from aiohttp import web
from chax import client
from chax import db
from chax import tasks

__version__ = "1.0.0"
__author__ = "Atavin Alexey"


def main():

    parser = argparse.ArgumentParser(description='Simple Web Chat')
    parser.add_argument('host', type=str, default='0.0.0.0', help='IPv4 address')
    parser.add_argument('port', type=int, default=8888, help='port')

    args = parser.parse_args()

    app = web.Application()
    database = db.RedisDB(host='0.0.0.0')
    api = client.API(db=database)
    app['api'] = api
    app.on_startup.append(tasks.start_tasks)
    app.on_cleanup.append(tasks.cleanup_tasks)
    app.router.add_post("/register/", api.register)
    app.router.add_post("/auth/", api.auth)
    web.run_app(app,
                host=args.host,
                port=int(args.port))

if __name__ == "__main__":
    main()
