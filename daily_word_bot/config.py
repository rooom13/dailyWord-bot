import os
from distutils.util import strtobool
from collections import namedtuple

from daily_word_bot import utils

Config = namedtuple("Config", [
    "ADMIN_CHAT_IDS",
    "BOT_TOKEN",
    "REDIS_HOST",
    "WORD_BANK_LOCAL",
    "VERSION",
])

live_config = Config(
    ADMIN_CHAT_IDS=utils.parse_admin_chat_ids_var(),
    BOT_TOKEN=os.getenv("BOT_TOKEN"),
    REDIS_HOST="redis",
    WORD_BANK_LOCAL=False,
    VERSION=os.getenv("VERSION")
)

test_config = Config(
    ADMIN_CHAT_IDS=utils.parse_admin_chat_ids_var(),
    BOT_TOKEN=os.getenv("TEST_BOT_TOKEN"),
    REDIS_HOST="localhost",
    WORD_BANK_LOCAL=strtobool(os.getenv("WORD_BANK_LOCAL") or "true"),
    VERSION="aVersion"
)

config = live_config if (os.getenv("ENV") or "").lower() == "live" else test_config
