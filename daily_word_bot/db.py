import typing
import redis
import json

from telegram import Message


class DAO:

    def __init__(self, host: str):
        port: int = 6379
        self.r: redis.Redis = redis.Redis(host=host, port=port)

    def save_user(self, message: Message):
        chat_id: str = message.chat.id
        name: str = message.chat.first_name
        levels: list = ['beginner', 'intermediate', 'advanced']
        self.r.sadd("users", chat_id)

        user_info = json.dumps(dict(
            name=name,
            isActive=True,
            levels=levels
        ))
        self.r.set(f"userInfo:{chat_id}", user_info)

    def set_user_inactive(self, message: Message):
        chat_id: str = message.chat.id
        name: str = message.chat.first_name
        levels: list = self.get_user_levels(chat_id)

        user_info = json.dumps(dict(
            name=name,
            isActive=False,
            levels=levels
        ))
        self.r.set(f"userInfo:{chat_id}", user_info)

    def get_user(self, chat_id: str) -> dict:
        user_info = self.r.get(f"userInfo:{chat_id}")
        return json.loads(user_info)

    def get_all_user_ids(self) -> typing.List[str]:
        return to_string_list(self.r.smembers("users"))

    def get_all_users(self) -> typing.Iterator[dict]:
        chat_ids = self.get_all_user_ids()
        for chat_id in chat_ids:
            yield dict(self.get_user(chat_id), chatId=chat_id)

    def get_all_active_users(self) -> typing.List[dict]:
        users = self.get_all_users()

        def is_active(x):
            return x["isActive"]
        return list(filter(is_active, users))

    def save_user_blocked_word(self, message, word_id):
        chat_id: str = message.chat.id
        self.r.sadd(f"blockedWords-{chat_id}", word_id)

    def remove_user_blocked_word(self, message, word_id):
        chat_id: str = message.chat.id
        self.r.srem(f"blockedWords-{chat_id}", word_id)

    def get_user_blocked_words(self, chat_id) -> typing.List[str]:
        return to_string_list(self.r.smembers(f"blockedWords-{chat_id}"))

    def get_user_levels(self, chat_id) -> typing.List[str]:
        user_info = self.get_user(chat_id)
        return user_info["levels"]

    def remove_user_level(self, chat_id, level) -> None:
        user_info = self.get_user(chat_id)
        levels = user_info["levels"]
        levels.remove(level)
        user_info["levels"] = levels
        user_info = json.dumps(user_info)
        self.r.set(f"userInfo:{chat_id}", user_info)

    def add_user_level(self, chat_id, level) -> None:
        user_info = self.get_user(chat_id)
        levels = user_info["levels"]
        levels.append(level)
        user_info["levels"] = levels
        user_info = json.dumps(user_info)
        self.r.set(f"userInfo:{chat_id}", user_info)


TypeSmembers = typing.Set[typing.Union[bytes, float, int, str]]


def to_string_list(li: TypeSmembers) -> typing.List[str]:
    return [i.decode("utf-8") for i in li]
