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
    REDIS_HOST=os.getenv("REDIS_HOST"),
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


def mask_value(value):
    if value is None:
        return "None"
    return f"{value[:2]}***{value[-2:]}"

# log every value but mask the BOT TOKEN & REDIS host by showing only the first and last 2 characters


masked_config = config._replace(
    BOT_TOKEN=mask_value(config.BOT_TOKEN),
    REDIS_HOST=mask_value(config.REDIS_HOST),
    BACKUP_FILE_PATH_IN=mask_value(config.BACKUP_FILE_PATH_IN),
    BACKUP_FOLDER_ID_OUT=mask_value(config.BACKUP_FOLDER_ID_OUT),
    BACKUP_FILE_ID_OUT=mask_value(config.BACKUP_FILE_ID_OUT),
    ADMIN_CHAT_IDS=mask_value(config.ADMIN_CHAT_IDS)
)
print(f"Using config: {masked_config}")
