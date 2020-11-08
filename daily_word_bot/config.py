from collections import namedtuple
import os

Config = namedtuple("Config", [
    "ADMIN_CHAT_ID",
    "BOT_TOKEN"])

live_config = Config(
    ADMIN_CHAT_ID=os.getenv("ADMIN_CHAT_ID"),
    BOT_TOKEN=os.getenv("BOT_TOKEN")
)

test_config = Config(
    ADMIN_CHAT_ID=os.getenv("ADMIN_CHAT_ID"),
    BOT_TOKEN=os.getenv("TEST_BOT_TOKEN")
)

config = live_config if (
    os.getenv("ENV") or "").lower() == "live" else test_config
