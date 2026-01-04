import pytest
import fakeredis
from unittest.mock import Mock, patch

from telegram import Message, Chat

from daily_word_bot.dao.redis_dao import RedisDAO
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


@pytest.fixture
def dao():
    """Create a RedisDAO instance with a fake Redis connection."""
    with patch('daily_word_bot.dao.redis_dao.redis.Redis') as mock_redis:
        # Mock the ping method to avoid connection attempts
        mock_instance = Mock()
        mock_instance.ping.return_value = True
        mock_redis.return_value = mock_instance

        # Create RedisDAO instance (won't actually connect)
        dao_instance = RedisDAO("redis")
        # Replace with fake Redis for actual testing
        dao_instance.r = fakeredis.FakeStrictRedis()
        yield dao_instance
        # Cleanup after each test
        dao_instance.r.flushall()


@pytest.fixture
def message():
    """Create a test message."""
    return Message(message_id=123456789, date="",
                   chat=Chat(
                       id=chat_id,
                       first_name=test_user_info["name"],
                       type=""))


def test_save_user(dao, message):
    dao.save_user(message, levels=[])
    user_info = dao.get_user(chat_id)
    active_users = dao.get_all_user_ids()

    assert test_user_info == user_info
    assert chat_id in active_users


def test_get_all_users(dao, message):
    dao.save_user(message, levels=[])
    users = list(dao.get_all_users())
    assert dict(test_user_info, chatId=chat_id) in users


@pytest.mark.parametrize("kwargs", [
    {"is_blocked": True},
    {"is_deactivated": True},
    {"is_kicked": True},
])
def test_set_user_inactive(dao, message, kwargs):
    dao.save_user(message, levels=[])
    active_users = dao.get_all_active_users()
    assert dict(test_user_info, chatId=chat_id, levels=[]) in active_users

    dao.set_user_inactive(chat_id, **kwargs)
    active_users = dao.get_all_active_users()
    assert [] == active_users


def test_set_get_remove_user_bocked_words_paginated(dao, message):
    dao.save_user_blocked_word(message, "wid0")
    next_page, blocked_words = dao.get_user_blocked_words_paginated(chat_id, page=0, page_size=10)
    assert blocked_words == ["wid0"]
    assert next_page == 0

    dao.remove_user_blocked_word(message, "wid0")
    next_page, blocked_words = dao.get_user_blocked_words_paginated(chat_id, page=0, page_size=10)
    assert blocked_words == []
    assert next_page == 0


def test_set_get_remove_user_bocked_words(dao, message):
    dao.save_user_blocked_word(message, "wid0")
    blocked_words = dao.get_user_blocked_words(chat_id)
    assert blocked_words == ["wid0"]

    dao.remove_user_blocked_word(message, "wid0")
    blocked_words = dao.get_user_blocked_words(chat_id)
    assert blocked_words == []


def test_get_add_remove_user_level(dao, message):
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
