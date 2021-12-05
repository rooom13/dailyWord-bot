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
    "BACKUP_FILE_PATH_IN",
    "BACKUP_FOLDER_ID_OUT",
    "BACKUP_FILE_ID_OUT"
])

live_config = Config(
    ADMIN_CHAT_IDS=utils.parse_admin_chat_ids_var(),
    BOT_TOKEN=os.getenv("BOT_TOKEN"),
    REDIS_HOST="redis",
    WORD_BANK_LOCAL=False,
    VERSION=os.getenv("VERSION"),
    BACKUP_FILE_PATH_IN=os.getenv("BACKUP_FILE_PATH_IN"),
    BACKUP_FOLDER_ID_OUT=os.getenv("BACKUP_FOLDER_ID_OUT"),
    BACKUP_FILE_ID_OUT=os.getenv("BACKUP_FILE_ID_OUT")
)

test_config = Config(
    ADMIN_CHAT_IDS=utils.parse_admin_chat_ids_var(),
    BOT_TOKEN=os.getenv("TEST_BOT_TOKEN"),
    REDIS_HOST="localhost",
    WORD_BANK_LOCAL=strtobool(os.getenv("WORD_BANK_LOCAL") or "true"),
    VERSION="aVersion",
    BACKUP_FILE_PATH_IN=os.getenv("BACKUP_FILE_PATH_IN"),
    BACKUP_FOLDER_ID_OUT=os.getenv("BACKUP_FOLDER_ID_OUT"),
    BACKUP_FILE_ID_OUT=os.getenv("BACKUP_FILE_ID_OUT")
)

config = live_config if (os.getenv("ENV") or "").lower() == "live" else test_config
