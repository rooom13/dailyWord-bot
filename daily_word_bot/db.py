from typing import Tuple, Iterator, List, Set, Union
import redis
import json
import logging
from telegram import Message


logger = logging.getLogger()


class DAO:

    def __init__(self, host: str):
        port: int = 6379
        logger.info(f"Initializing Redis connection to {host}:{port} with SSL")

        # ElastiCache Serverless requires TLS/SSL
        self.r: redis.Redis = redis.Redis(
            host=host,
            port=port,
            ssl=True,
            ssl_cert_reqs=None,  # Don't verify certificates for ElastiCache Serverless
            socket_connect_timeout=10,
            socket_timeout=10,
            socket_keepalive=True,
            health_check_interval=30,
            retry_on_timeout=True,
            decode_responses=False
        )

        try:
            logger.info("Attempting to ping Redis...")
            response = self.r.ping()
            logger.info(f"Successfully connected to Redis. Ping response: {response}")
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}", exc_info=True)
            raise
        except redis.exceptions.TimeoutError as e:
            logger.error(f"Redis connection timeout: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to Redis: {e}", exc_info=True)
            raise

    def save_user(self, message: Message, levels: list):
        chat_id: str = message.chat.id
        name: str = message.chat.first_name
        self.r.sadd("users", chat_id)

        user_info = json.dumps(dict(
            name=name,
            isActive=True,
            isBlocked=False,
            isDeactivated=False,
            isKicked=False,
            levels=levels
        ))
        self.r.set(f"userInfo:{chat_id}", user_info)

    def set_user_inactive(self, chat_id: str,
                          is_blocked: bool = False,
                          is_deactivated: bool = False,
                          is_kicked: bool = False
                          ):
        user_info: dict = self.get_user(chat_id)
        user_info["isActive"] = False
        if is_blocked:
            user_info["isBlocked"] = True
        if is_deactivated:
            user_info["isDeactivated"] = True
        if is_kicked:
            user_info["isKicked"] = True

        self.r.set(f"userInfo:{chat_id}", json.dumps(user_info))

    def get_user(self, chat_id: str) -> dict:
        user_info = self.r.get(f"userInfo:{chat_id}")
        user_info = json.loads(user_info) if user_info else {}
        return user_info

    def get_all_user_ids(self) -> List[str]:
        return to_string_list(self.r.smembers("users"))

    def get_all_users(self) -> Iterator[dict]:
        chat_ids = self.get_all_user_ids()
        for chat_id in chat_ids:
            yield dict(self.get_user(chat_id), chatId=chat_id)

    def get_all_active_users(self) -> List[dict]:
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

    def get_user_blocked_words(self, chat_id) -> List[str]:
        return to_string_list(self.r.smembers(f"blockedWords-{chat_id}"))

    def get_count_blocked_words(self, chat_id: str) -> int:
        return self.r.scard(f"blockedWords-{chat_id}")

    def get_user_blocked_words_paginated(self, chat_id: str, page: int, page_size: int) -> Tuple[int, List[str]]:
        cursor, word_ids = self.r.sscan(f"blockedWords-{chat_id}", cursor=page, count=page_size)
        return cursor, to_string_list(word_ids)

    def get_user_levels(self, chat_id) -> List[str]:
        user_info = self.get_user(chat_id)
        user_levels = user_info.get("levels", [])
        return user_levels

    def remove_user_level(self, chat_id, level) -> None:
        user_info = self.get_user(chat_id)
        levels = user_info.get("levels", [])
        levels.remove(level)
        user_info.update({"levels": levels})
        user_info = json.dumps(user_info)
        self.r.set(f"userInfo:{chat_id}", user_info)

    def add_user_level(self, chat_id, level) -> None:
        user_info = self.get_user(chat_id)
        levels = user_info.get("levels", [])
        levels.append(level)
        user_info.update({"levels": levels})
        user_info = json.dumps(user_info)
        self.r.set(f"userInfo:{chat_id}", user_info)


TypeSmembers = Set[Union[bytes, float, int, str]]


def to_string_list(li: TypeSmembers) -> List[str]:
    return [i.decode("utf-8") for i in li]
