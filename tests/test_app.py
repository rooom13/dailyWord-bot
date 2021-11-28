from copy import copy

import pytest
from unittest.mock import MagicMock

from telegram.error import Unauthorized

from daily_word_bot.app import App


def test_is_admin():
    assert isinstance(App.is_admin("123"), bool)


@pytest.fixture
def app():
    app = App()
    app.dao = MagicMock()
    return app


@pytest.fixture
def app_unauthorized_user(mocker, app):
    app_ = copy(app)
    app_.updater = MagicMock()
    app_.updater.bot.send_message = MagicMock(side_effect=Unauthorized("blocked"))
    return app_


@pytest.fixture
def app_unknown_unauthorized_user(mocker, app):
    app_ = copy(app)
    app_.updater = MagicMock()
    app_.updater.bot.send_message = MagicMock(side_effect=Unauthorized("something unknown"))
    return app_


def test_send_message_to_user(app_unauthorized_user, app_unknown_unauthorized_user):
    user = dict(chatId="123", name="name")
    app_unauthorized_user.send_message_to_user(user=user, msg="a-msg")

    with pytest.raises(Unauthorized):
        app_unknown_unauthorized_user.send_message_to_user(user=user, msg="a-msg")
