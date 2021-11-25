import re
import typing
from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup

from daily_word_bot import utils

POSSIBLE_USER_LEVELS: list = ['beginner', 'intermediate', 'advanced']


def highlight(w: str) -> str:
    return f"<b>{w}</b>"


def build_levels_answer(user_levels: list) -> dict:
    # build the message and send it back to the user
    msg = "🛠 Choose the level of the words to be sent.\nClick the empty checkbox ⬜️ to assign or the filled one ✅ to unassign a level. 🛠\n\nThese are your word levels: "

    # create inline keyboard buttons
    inline_keyboard_buttons = []
    for level in POSSIBLE_USER_LEVELS:
        if level not in user_levels:
            level_message = '⬜️ ' + level
            callback_data = f'/addlevel {level}'
        else:
            level_message = '✅ ' + level
            callback_data = f'/removelevel {level}'

        inline_keyboard_buttons.append([InlineKeyboardButton(level_message, callback_data=callback_data)])

    # reply markup answer object
    reply_markup = InlineKeyboardMarkup(inline_keyboard_buttons)

    return {'msg': msg, 'reply_markup': reply_markup}


def get_terms_without_articles(terms: str) -> typing.List[str]:
    # quitar artculos
    regex = r"die |das |der |el |la "
    terms_without_articles: typing.List[str] = [re.sub(regex, "", t, flags=re.IGNORECASE) for t in terms.split("/")]
    return terms_without_articles


def highlight_in_sentence(s: str, terms: str) -> str:

    # highlight terms
    terms_without_articles = get_terms_without_articles(terms)
    for t in terms_without_articles:
        s = re.sub(f"({t})", r"<b>\1</b>", s, flags=re.IGNORECASE)
    return s


broadcast_sep = f"\n{'-'*10}\n"


def build_broadcast_preview_msg(msg: str) -> str:
    return f"Broadcast message preview:{broadcast_sep}{msg}{broadcast_sep}Do you want to send it?"


def get_broadcast_msg_from_preview(msg: str) -> str:
    return msg.split(broadcast_sep)[1]


def build_word_msg(word_data: dict) -> str:

    examples: list = (word_data.get("examples") or [])
    word_de = word_data.get("de", "")
    word_es = word_data.get("es", "")

    examples_str: str = ("\n".join([(
        f"\n🇩🇪 {utils.highlight_in_sentence(ex.get('de', ''), word_de)}"
        f"\n🇪🇸 {utils.highlight_in_sentence(ex.get('es', ''), word_es)}"
    ) for ex in examples]))

    return (
        f"\n🇩🇪 {word_de}"
        f"\n🇪🇸 {word_es}"
        f"\n{examples_str}"
    )


def build_available_commands_msg(bot_commands: typing.List[BotCommand]) -> str:
    commands_str = "\n".join([f"{c.command} ➜ {c.description}" for c in bot_commands])
    return "Available commands:\n" + commands_str


def build_users_msg(users: typing.List[dict]) -> str:
    users_str = "\n".join(f'- {u.get("chatId")} {u.get("name")} {"😀" if u.get("isActive")  else  "😴"}' for u in users)
    msg = f"Users: ({len(users)})\n{users_str}"
    return msg
