import logging
import os

import yaml

CONFIG_FILENAME = "/etc/chax.yaml"

with open(os.path.dirname(os.path.realpath(__file__)) + "/defaults.yaml", "r") as file:
    CONF = yaml.load(file.read())

try:
    with open(CONFIG_FILENAME, "r") as file:
        defaults = yaml.load(file.read())
        CONF.update(defaults)
except FileNotFoundError:
    pass
except yaml.YAMLError and ValueError:
    logging.critical(f"Configuration file problem. Check {CONFIG_FILENAME}."
                     f"Application started with default config.")

LOGGING_CONFIG = CONF['logging']

logging.basicConfig(level=LOGGING_CONFIG['level'],
                    format='%(asctime)s %(name)s (%(threadName)s) %(message)s',
                    filename=print())

REDIS_HOST = os.environ.get("REDISHOST", None) or CONF['redis']['host']
REDIS_PORT = os.environ.get("REDISPORT", None) or CONF['redis']['port']

REDIS_CHANNEL = CONF['redis']['channel']
REDIS_MEMBERS_KEY = CONF['redis']['members_key']
WEB_HOST = CONF['web']['host']
WEB_PORT = CONF['web']['port']
MESSAGE_HANDLERS = CONF['internal']['message_handlers']
