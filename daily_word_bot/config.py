from collections import namedtuple
import os

Config = namedtuple("Config", [
    "ADMIN_CHAT_ID",
    "BOT_TOKEN",
    "REDIS_HOST"])

live_config = Config(
    ADMIN_CHAT_ID=os.getenv("ADMIN_CHAT_ID"),
    BOT_TOKEN=os.getenv("BOT_TOKEN"),
    REDIS_HOST="redis"
)

test_config = Config(
    ADMIN_CHAT_ID=os.getenv("ADMIN_CHAT_ID"),
    BOT_TOKEN=os.getenv("TEST_BOT_TOKEN"),
    REDIS_HOST="localhost"
)

config = live_config if (os.getenv("ENV") or "").lower() == "live" else test_config

