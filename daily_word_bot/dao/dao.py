from abc import ABC, abstractmethod
from telegram import Message
from typing import Tuple, Iterator, List


class DAO(ABC):

    @abstractmethod
    def save_user(self, message: Message, levels: list):
        pass  # pragma: no cover

    @abstractmethod
    def set_user_inactive(self, chat_id: str,
                          is_blocked: bool = False,
                          is_deactivated: bool = False,
                          is_kicked: bool = False
                          ):
        pass  # pragma: no cover

    @abstractmethod
    def get_user(self, chat_id: str) -> dict:
        pass  # pragma: no cover

    @abstractmethod
    def get_all_user_ids(self) -> list[str]:
        pass  # pragma: no cover

    @abstractmethod
    def get_all_users(self) -> Iterator[dict]:
        pass  # pragma: no cover

    @abstractmethod
    def get_all_active_users(self) -> list[dict]:
        pass  # pragma: no cover

    @abstractmethod
    def save_user_blocked_word(self, message, word_id):
        pass  # pragma: no cover

    @abstractmethod
    def remove_user_blocked_word(self, message, word_id):
        pass  # pragma: no cover

    @abstractmethod
    def get_user_blocked_words(self, chat_id) -> List[str]:
        pass  # pragma: no cover

    @abstractmethod
    def get_count_blocked_words(self, chat_id: str) -> int:
        pass  # pragma: no cover

    @abstractmethod
    def get_user_blocked_words_paginated(self, chat_id: str, page: int, page_size: int) -> Tuple[int, List[str]]:
        pass  # pragma: no cover

    @abstractmethod
    def get_user_levels(self, chat_id) -> List[str]:
        pass  # pragma: no cover
