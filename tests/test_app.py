from copy import copy

import pytest
from unittest.mock import MagicMock, patch

from telegram.error import Unauthorized

from daily_word_bot.app import App
from daily_word_bot import utils


def test_is_admin():
    assert isinstance(App.is_admin("123"), bool)


@pytest.fixture
def app():
    utils.fetch_contributors = MagicMock()
    # Mock DAO to avoid Redis connection during App initialization
    with patch('daily_word_bot.app.DAO') as mock_dao:
        mock_dao.return_value = MagicMock()
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


def test_word_bank_property(app):
    """Test that word_bank property lazy loads and returns WordBank instance."""
    with patch('daily_word_bot.app.WordBank') as mock_wordbank_class:
        mock_wordbank_instance = MagicMock()
        mock_wordbank_class.return_value = mock_wordbank_instance

        # First access should create the instance
        result1 = app.word_bank
        assert result1 == mock_wordbank_instance
        mock_wordbank_class.assert_called_once()

        # Second access should return the cached instance
        result2 = app.word_bank
        assert result2 == mock_wordbank_instance
        # Should still be called only once (lazy loading)
        mock_wordbank_class.assert_called_once()


def test_contributors_property(app):
    """Test that contributors property lazy loads and returns list of contributors."""
    mock_contributors = ['contributor1', 'contributor2', 'contributor3']

    with patch('daily_word_bot.utils.fetch_contributors', return_value=mock_contributors):
        # First access should fetch contributors
        result1 = app.contributors
        assert result1 == mock_contributors

        # Second access should return the cached list
        result2 = app.contributors
        assert result2 == mock_contributors
        assert result1 is result2  # Same object reference (cached)
