import pytest
import fakeredis

from telegram import Message, Chat

from daily_word_bot.config import config
from daily_word_bot.db import DAO
from daily_word_bot import utils


chat_id = "123"
test_user_info = dict(
    name="Pepe",
    isActive=True,
    isDeactivated=False,
    isBlocked=False,
    isKicked=False,
    levels=[]
)
dao = DAO(config.REDIS_HOST)
dao.r = fakeredis.FakeStrictRedis()
message = Message(message_id=123456789, date="",
                  chat=Chat(
                      id=chat_id,
                      first_name=test_user_info["name"],
                      type=""))


def test_save_user():
    dao.save_user(message, levels=[])
    user_info = dao.get_user(chat_id)
    active_users = dao.get_all_user_ids()

    assert test_user_info == user_info
    assert chat_id in active_users
    dao.r.flushall()


def test_get_all_users():
    dao.save_user(message, levels=[])
    users = list(dao.get_all_users())
    assert dict(test_user_info, chatId=chat_id) in users
    dao.r.flushall()


@pytest.mark.parametrize("kwargs", [
    {"is_blocked": True},
    {"is_deactivated": True},
    {"is_kicked": True},
])
def test_set_user_inactive(kwargs):
    dao.save_user(message, levels=[])
    active_users = dao.get_all_active_users()
    assert dict(test_user_info, chatId=chat_id, levels=[]) in active_users

    dao.set_user_inactive(chat_id, **kwargs)
    active_users = dao.get_all_active_users()
    assert [] == active_users
    dao.r.flushall()


def test_set_get_remove_user_bocked_words_paginated():
    dao.save_user_blocked_word(message, "wid0")
    next_page, blocked_words = dao.get_user_blocked_words_paginated(chat_id, page=0, page_size=10)
    assert blocked_words == ["wid0"]
    assert next_page == 0

    dao.remove_user_blocked_word(message, "wid0")
    next_page, blocked_words = dao.get_user_blocked_words_paginated(chat_id, page=0, page_size=10)
    assert blocked_words == []
    assert next_page == 0

    dao.r.flushall()


def test_set_get_remove_user_bocked_words():
    dao.save_user_blocked_word(message, "wid0")
    blocked_words = dao.get_user_blocked_words(chat_id)
    assert blocked_words == ["wid0"]

    dao.remove_user_blocked_word(message, "wid0")
    blocked_words = dao.get_user_blocked_words(chat_id)
    assert blocked_words == []

    dao.r.flushall()


def test_get_add_remove_user_level():
    levels_to_remove = list(utils.POSSIBLE_USER_LEVELS)
    level_to_add = 'advanced'
    test_levels = list(utils.POSSIBLE_USER_LEVELS)
    levels = dao.get_user_levels(chat_id)
    user_levels = levels if len(levels) > 0 else list(utils.POSSIBLE_USER_LEVELS)

    dao.save_user(message, user_levels)

    for level_to_remove in levels_to_remove:
        dao.remove_user_level(chat_id, level_to_remove)
        test_levels.remove(level_to_remove)

    dao.add_user_level(chat_id, level_to_add)
    test_levels.append(level_to_add)
    levels = dao.get_user_levels(chat_id)

    assert test_levels == levels
