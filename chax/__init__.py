import argparse
import sys
from aiohttp import web
from .api import API
from .db import RedisDB

__version__ = "1.0.0"
__author__ = "Atavin Alexey"


def main():

    parser = argparse.ArgumentParser(description='Simple Web Chat')
    parser.add_argument('host', type=str, default='0.0.0.0', help='IPv4 address')
    parser.add_argument('port', type=int, default=8888, help='port')

    args = parser.parse_args()

    app = web.Application()
    database = RedisDB(host='0.0.0.0')
    api = API(db=database)

    app.router.add_post("/register/", api.register)
    app.router.add_port("/auth/", api.auth)
    web.run_app(app,
                host=app['host'],
                port=int(app['port']))

if __name__ == "__main__":
    main()
