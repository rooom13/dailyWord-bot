import os
from distutils.util import strtobool
from collections import namedtuple

Config = namedtuple("Config", [
    "ADMIN_CHAT_ID",
    "BOT_TOKEN",
    "REDIS_HOST",
    "WORD_BANK_LOCAL",
    "VERSION",
])

live_config = Config(
    ADMIN_CHAT_ID=os.getenv("ADMIN_CHAT_ID"),
    BOT_TOKEN=os.getenv("BOT_TOKEN"),
    REDIS_HOST="redis",
    WORD_BANK_LOCAL=False,
    VERSION=False
)

test_config = Config(
    ADMIN_CHAT_ID=os.getenv("ADMIN_CHAT_ID"),
    BOT_TOKEN=os.getenv("TEST_BOT_TOKEN"),
    REDIS_HOST="localhost",
    WORD_BANK_LOCAL=strtobool(os.getenv("WORD_BANK_LOCAL") or "false"),
    VERSION="aVersion"
)

config = live_config if (os.getenv("ENV") or "").lower() == "live" else test_config
