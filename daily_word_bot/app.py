import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

from daily_word_bot.config import config
from daily_word_bot import utils
from daily_word_bot.db import DAO

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

dao = DAO()

available_commands = (
    "Available commands:"
    "\n· /help   ➡ Opens this help section"
    "\n· /stop   ➡ Stops me sending words"
    "\n· /start  ➡ Makes me start sending words"
)


def on_help_callback(update: Update, context: CallbackContext) -> None:
    msg = available_commands
    update.message.reply_text(msg)


def on_users_callback(update: Update, context: CallbackContext) -> None:
    if str(update.message.chat_id) == config.ADMIN_CHAT_ID:
        users = list(dao.get_all_users())
        users_str = "\n".join(f'- {u.get("chatId")} {u.get("name")} {"😀" if u.get("isActive")  else  "😴"}' for u in users)
        msg = f"Users: ({len(users)})\n{users_str}"
        update.message.reply_text(msg)
    else:
        msg = "Loitering around my github?\nDon't hesitate greeting me! 😀"
        update.message.reply_text(msg)


def on_start_callback(update: Update, context: CallbackContext, is_inline_keyboard=False) -> None:
    message = update.message or update.callback_query.message
    dao.save_user(message)

    msg = f"Hello {message.chat.first_name}! " + available_commands
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("/stop", callback_data='/stop')]
    ])

    if is_inline_keyboard:
        update.callback_query.edit_message_text(msg, reply_markup=reply_markup)
    else:
        update.message.reply_text(msg, reply_markup=reply_markup)


def on_stop_callback(update: Update, context: CallbackContext, is_inline_keyboard=False) -> None:
    message = update.message or update.callback_query.message
    dao.set_user_inactive(message)

    msg = "You will no longer receive words!\n...Unles you use /start"
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("/start", callback_data='/start')]
    ])

    if is_inline_keyboard:
        update.callback_query.edit_message_text(msg, reply_markup=reply_markup)
    else:
        update.message.reply_text(msg, reply_markup=reply_markup)


def inline_keyboard_callbacks(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    callback_data = query.data
    if callback_data == "/start":
        on_start_callback(update, context, is_inline_keyboard=True)
    elif callback_data == "/stop":
        on_stop_callback(update, context, is_inline_keyboard=True)


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


def send_word(context: CallbackContext):

    word_data: dict = {
        "de": "zittern",
        "es": "tiritar/temblar",
        "examples": [
            {
                "de": "Vor Kälte zu zittern",
                "es": "Temblar de frío"
            },
            {
                "de": "Vor Angst zu zittern",
                "es": "Tiritar de miedo"
            }
        ]
    }

    msg: str = build_word_msg(word_data)

    chat_ids = dao.get_all_user_ids()
    for chat_id in chat_ids:
        context.bot.send_message(chat_id=chat_id, text=msg, parse_mode='HTML')


def run():
    """Run bot"""

    updater = Updater(config.BOT_TOKEN)

    updater.job_queue.run_custom(send_word, job_kwargs=dict(
        trigger="cron",
        day="*",
        hour="10,18,20",
        minute=30,
        # second="10,20,30,40,50,0" # test
    ))

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", on_start_callback))
    dispatcher.add_handler(CommandHandler("stop", on_stop_callback))
    dispatcher.add_handler(CommandHandler("help", on_help_callback))
    dispatcher.add_handler(CommandHandler("users", on_users_callback))
    dispatcher.add_handler(CallbackQueryHandler(inline_keyboard_callbacks))

    updater.start_polling()
    updater.idle()
