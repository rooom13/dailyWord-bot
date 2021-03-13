import typing
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot, BotCommand
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

from daily_word_bot.config import config
from daily_word_bot import utils
from daily_word_bot.db import DAO
from daily_word_bot.word_bank import WordBank

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

dao: typing.Union[DAO, None] = None
word_bank: typing.Union[WordBank, None] = None


user_bot_commands = [
    BotCommand("/help", "Opens help section"),
    BotCommand("/start", "Starts sending words"),
    BotCommand("/stop", "Stops sending words"),
    BotCommand("/blockedwords", "Shows your blocked words")
]

available_commands_msg = utils.build_available_commands_msg(user_bot_commands)


def on_help_callback(update: Update, context: CallbackContext) -> None:  # pragma: no cover
    update.message.reply_text(available_commands_msg)


def on_users_callback(update: Update, context: CallbackContext) -> None:  # pragma: no cover
    if str(update.message.chat_id) == config.ADMIN_CHAT_ID:
        users = list(dao.get_all_users())
        msg = utils.build_users_msg(users)
    else:
        msg = "Loitering around my github?\nDon't hesitate greeting me! 😀"
    update.message.reply_text(msg)


def on_wordbankinfo_callback(update: Update, context: CallbackContext) -> None:  # pragma: no cover
    msg = f"Word bank info:\n - {len(word_bank.df.index)} words, last updated on {word_bank.last_updated_at}"
    update.message.reply_text(msg)


def on_start_callback(update: Update, context: CallbackContext, is_inline_keyboard=False) -> None:  # pragma: no cover
    message = update.message or update.callback_query.message
    dao.save_user(message)

    msg = f"Hello {message.chat.first_name}! " + available_commands_msg
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("/stop", callback_data='/stop')]
    ])

    if is_inline_keyboard:
        update.callback_query.edit_message_text(msg, reply_markup=reply_markup)
    else:
        update.message.reply_text(msg, reply_markup=reply_markup)


def on_stop_callback(update: Update, context: CallbackContext, is_inline_keyboard=False) -> None:  # pragma: no cover
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


def on_get_blockwords_callback(update: Update, context: CallbackContext, is_inline_keyboard=False) -> None: # pragma: no cover
    message = update.message or update.callback_query.message
    
    chat_id = message.chat_id

    blocked_word_ids = dao.get_user_blocked_words(chat_id)
    blocked_words = word_bank.get_words(blocked_word_ids)
        
    words_str = ""
    
    inline_keyboard_buttons = []

    for blocked_word in blocked_words:
        word_id = blocked_word[0]
        german_word = blocked_word[1]
        spanish_word = blocked_word[2]
        spanish_and_german_word = "🇪🇸" + spanish_word + " | " + "🇩🇪" + german_word
        inline_keyboard_buttons.append([InlineKeyboardButton(spanish_and_german_word,  callback_data=f'/unblockword_from_blocked_words {word_id}')])
      

    reply_markup = InlineKeyboardMarkup(inline_keyboard_buttons)
    
    msg = "These are your blocked words. Click to unblock them." if inline_keyboard_buttons else "You don't have any blocked words."
   
    if is_inline_keyboard:
        update.callback_query.edit_message_text(msg, reply_markup=reply_markup)
    else:
        update.message.reply_text(msg, reply_markup=reply_markup)


def inline_keyboard_callbacks(update: Update, context: CallbackContext) -> None:  # pragma: no cover
    query = update.callback_query
    query.answer()

    callback_data = query.data.split(" ")

    if len(callback_data) == 1:
        if callback_data == "/start":
            on_start_callback(update, context, is_inline_keyboard=True)
        elif callback_data == "/stop":
            on_stop_callback(update, context, is_inline_keyboard=True)
    elif len(callback_data) == 2:
        command: str = callback_data[0]
        word_id: str = callback_data[1]
        if command == "/blockword":
            dao.save_user_blocked_word(update.callback_query.message, word_id)
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Zurücknehmen - Deshacer", callback_data=f"/unblockword {word_id}")]
            ])
            msg = "✅\n" + update.callback_query.message.text
            update.callback_query.edit_message_text(msg, reply_markup=reply_markup)
        elif command == "/unblockword":
            dao.remove_user_blocked_word(update.callback_query.message, word_id)
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Gelernt! - Aprendida!", callback_data=f"/blockword {word_id}")]
            ])
            msg = update.callback_query.message.text[2:]  # remove '✅\n'
            update.callback_query.edit_message_text(msg, reply_markup=reply_markup)
        elif command == "/blockword_from_blocked_words":
            dao.save_user_blocked_word(update.callback_query.message, word_id)
            on_get_blockwords_callback(update, context, is_inline_keyboard=True)
        elif command == "/unblockword_from_blocked_words":
            dao.remove_user_blocked_word(update.callback_query.message, word_id)
            on_get_blockwords_callback(update, context, is_inline_keyboard=True)


def send_word(context: CallbackContext):  # pragma: no cover
    users = dao.get_all_active_users()
    logger.info(f"sending words to {len(users)} users")

    for user in users:
        try:
            chat_id = user["chatId"]
            exclude = dao.get_user_blocked_words(chat_id)
            word_data = word_bank.get_random(exclude=exclude)

            msg: str = utils.build_word_msg(word_data)

            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Gelernt! - Aprendida!", callback_data=f"/blockword {word_data['word_id']}")]
            ])

            context.bot.send_message(chat_id=chat_id, text=msg, parse_mode='HTML', reply_markup=reply_markup)
        except Exception as e:
            logger.error("shit", exc_info=e)


def run():  # pragma: no cover
    """Run bot"""
    logger.info("Started app")

    global dao, word_bank

    dao = DAO(config.REDIS_HOST)
    word_bank = WordBank(config.WORD_BANK_LOCAL)

    updater = Updater(config.BOT_TOKEN)
    updater.bot.set_my_commands(user_bot_commands)

    updater.job_queue.run_custom(send_word, job_kwargs=dict(
        trigger="cron",
        day="*",
        hour="10,18,20",
        minute="30",
        # second="10,20,30,40,50,0"  # test
    ))
    updater.job_queue.run_custom(lambda x: word_bank.update(), job_kwargs=dict(
        trigger="cron",
        day="*",
        hour="7",
        # second="10,20,30,40,50,0"  # test
    ))

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", on_start_callback))
    dispatcher.add_handler(CommandHandler("stop", on_stop_callback))
    dispatcher.add_handler(CommandHandler("help", on_help_callback))
    dispatcher.add_handler(CommandHandler("users", on_users_callback))
    dispatcher.add_handler(CommandHandler("wordbankinfo", on_wordbankinfo_callback))
    dispatcher.add_handler(CommandHandler("blockedwords", on_get_blockwords_callback))
    dispatcher.add_handler(CallbackQueryHandler(inline_keyboard_callbacks))

    updater.start_polling()
    updater.idle()
