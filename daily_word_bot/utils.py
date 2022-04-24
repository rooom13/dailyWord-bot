import re
import os
from collections import defaultdict
from typing import List, Dict
from datetime import datetime
import requests
from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup

from daily_word_bot import utils

POSSIBLE_USER_LEVELS: tuple = ('beginner', 'intermediate', 'advanced')


def highlight(w: str) -> str:
    return f"<b>{w}</b>"


def user_to_string(user: dict) -> str:
    chat_id = user.get("chatId")
    name = user.get("name")
    is_active = "😀" if user.get("isActive") else "😴"
    is_blocked = "⛔" if user.get("isBlocked") else ""
    is_deactivated = "📵" if user.get("isDeactivated") else ""
    is_kicked = "🥾" if user.get("isKicked") else ""
    levels = "".join(f"{level[0]}" for level in user.get("levels") or [])

    return (f"- {chat_id} {name} {is_active}{is_blocked}{is_deactivated}{is_kicked}" + (f" <i>{levels}</i>" if levels else ""))


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


def get_terms_without_articles(terms: str) -> List[str]:
    # quitar artculos
    regex = r"die |das |der |el |la "
    terms_without_articles: List[str] = [re.sub(regex, "", t, flags=re.IGNORECASE) for t in terms.split("/")]
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


def build_available_commands_msg(bot_commands: List[BotCommand]) -> str:
    commands_str = "\n".join([f"{c.command} ➜ {c.description}" for c in bot_commands])
    return "Available commands:\n" + commands_str


hero_char = "🦸🏿‍♀️"


def convert_to_hyperlink(url: str, text: str) -> str:
    return f"<a href=\"{url}\">{text}</a>"


def convert_to_github_hyperlink(contributor_name: str) -> str:
    return convert_to_hyperlink(f"https://github.com/{contributor_name}", contributor_name)


def build_info_msg(version: str, start_date: datetime,
                   word_bank_length: int, word_bank_update_date: datetime,
                   contributors: List[Dict]) -> str:
    str_contributors = "\n".join([f" {hero_char} {utils.convert_to_github_hyperlink(c['login'])}" for c in contributors if c['type'] != 'Bot'])
    return (
        f"Version: <i>{version}</i> deployed on {start_date}"
        "\n"
        f"\nWord bank info:\n - {word_bank_length} words, last updated on {word_bank_update_date}"
        "\n"
        f"\n Project hero contributors who deserve a cape:  \n{str_contributors}"
    )


def build_users_msg(users: List[dict]) -> str:

    users_classified = defaultdict(list)

    # tuple with user classification key & bool function that classifies
    # note that order matters, that's why 'active' is the last one with a constant True
    classifications = [
        ("deactivated", lambda u: u.get("isDeactivated")),
        ("blocked", lambda u: u.get("isBlocked")),
        ("kicked", lambda u: u.get("isKicked")),
        ("stopped", lambda u: not u.get("isActive")),
        ("active", lambda u: True)
    ]

    for u in users:
        for key, classification_fun in classifications:
            if classification_fun(u):
                users_classified[key].append(u)
                break

    msg = f"Total users: ({len(users)})"

    for key, _ in classifications:
        users_c = users_classified[key]
        msg += f"\n\n<b>{key}</b> ({len(users_c)})\n" + "\n".join([utils.user_to_string(user) for user in users_c])

    return msg


def parse_admin_chat_ids_var() -> List[str]:
    return (os.getenv("ADMIN_CHAT_IDS") or "").split(",")


def fetch_contributors() -> List[str]:  # pragma: no cover
    try:
        return requests.get("https://api.github.com/repos/rooom13/dailyWord-bot/contributors").json()
    except Exception:
        return []
