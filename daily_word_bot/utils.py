import re
import typing
from telegram import BotCommand

from daily_word_bot import utils

POSSIBLE_USER_LEVELS: list = ['beginner', 'intermediate', 'advanced']


def highlight(w: str) -> str:
    return f"<b>{w}</b>"


def get_level_from_command(command: str) -> str:
    # variable to store the extracted level from the command
    extracted_level = ''

    # command parts sent by the user
    command_parts = command.split(maxsplit=1)

    # check result of the split
    if len(command_parts) == 2:  # if user specified a level
        extracted_level = command_parts[1]

    return extracted_level


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
