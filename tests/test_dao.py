import unittest
import fakeredis

from telegram import Message, Chat

from daily_word_bot.config import config
from daily_word_bot.db import DAO

tc = unittest.TestCase()

chat_id = "123"
test_user_info = dict(
    name="Pepe",
    isActive=True
)
dao = DAO(config.REDIS_HOST)
dao.r = fakeredis.FakeStrictRedis()
message = Message(message_id=123456789, date="",
                  chat=Chat(
                      id=chat_id,
                      first_name=test_user_info["name"],
                      type=""))


def test_save_user():
    dao.save_user(message)
    user_info = dao.get_user(chat_id)
    active_users = dao.get_all_user_ids()

    tc.assertDictEqual(test_user_info, user_info)
    tc.assertIn(chat_id, active_users)
    dao.r.flushall()


def test_get_all_users():
    dao.save_user(message)
    users = list(dao.get_all_users())
    tc.assertIn(dict(test_user_info, chatId=chat_id), users)
    dao.r.flushall()


def test_set_user_inactive():
    dao.save_user(message)
    active_users = dao.get_all_active_users()
    tc.assertIn(dict(test_user_info, chatId=chat_id), active_users)

    dao.set_user_inactive(message)
    active_users = dao.get_all_active_users()
    tc.assertEqual([], active_users)


def test_set_get_remove_user_bocked_words():
    dao.save_user_blocked_word(message, "wid0")
    blocked_words = dao.get_user_blocked_words(chat_id)
    tc.assertEqual(blocked_words, ["wid0"])

    dao.remove_user_blocked_word(message, "wid0")
    blocked_words = dao.get_user_blocked_words(chat_id)
    tc.assertEqual(blocked_words, [])

    dao.r.flushall()
