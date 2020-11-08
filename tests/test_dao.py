import unittest
import pytest

from telegram import Message, Chat

from daily_word_bot.db import DAO

tc = unittest.TestCase()

chat_id = "1233"
test_user_info = dict(
    name="Pepe",
    isActive=True
)
dao = DAO()

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
    dao._drop_db()


def test_get_all_users():
    dao.save_user(message)
    users = dao.get_all_users()

    tc.assertIn(test_user_info, users)
    dao._drop_db()
