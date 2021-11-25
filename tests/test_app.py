from daily_word_bot.app import App


def test_is_admin():
    assert isinstance(App.is_admin("123"), bool)


def test_app():
    App()
