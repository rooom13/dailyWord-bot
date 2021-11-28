import html

from functools import wraps
import typing
import traceback
import logging
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.error import Unauthorized
from telegram.ext import (Updater,
                          CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler,
                          CallbackContext,
                          Filters)

from daily_word_bot.config import config
from daily_word_bot import utils
from daily_word_bot.db import DAO
from daily_word_bot.word_bank import WordBank
from daily_word_bot.backup_service import BackupService

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
    BotCommand("/blockedwords", "Shows your blocked words"),
    BotCommand("/mylevels", "Shows your preferred levels of the words to be sent. Possible word levels are: beginner, intermediate and advanced")
]

available_commands_msg = utils.build_available_commands_msg(user_bot_commands)


def admin_only(func):  # pragma: no cover
    """If current user is not admin, don't execute the method & send admin msg"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        update = args[1]
        if self.is_admin(update.effective_message.chat.id):
            return func(*args, **kwargs)
        else:
            update.effective_message.reply_text(self.admin_msg, parse_mode='HTML')
    return wrapper


def handle_error_send_user(func):

    @wraps(func)
    def wrapper(self, user, *kargs, **kwargs):
        chat_id, name = user["chatId"], user["name"]
        try:
            try:
                return func(self, user, *kargs, **kwargs)
            # On recongized Unauthorized, we set the user inactive
            except Unauthorized as e:
                is_blocked = "blocked" in e.message
                is_deactivated = "deactivated" in e.message
                if not (is_blocked or is_deactivated):
                    raise e
                self.dao.set_user_inactive(chat_id, is_blocked, is_deactivated)

        # Any other errors must be reported
        except Exception as e:
            logger.error("An exception occurred", exc_info=e)
            exception_str = traceback.format_exc()
            self.send_message_to_admins(f"An exception occured in <i>send_message_to_user</i> "
                                        f"to user: {chat_id} - {name}"
                                        f"\n\n<pre>{exception_str}</pre>")
    return wrapper


class States:
    BROADCAST_TYPE = 0
    BROADCAST_CONFIRM = 1


class Buttons:
    cancel = [[InlineKeyboardButton("/cancel", callback_data="/cancel")]]


class App:

    ####################
    # Common msgs      #
    ####################
    admin_msg = "This command is reserved for <pre>admins</pre> 😏😏"

    ####################
    # Callbacks        #
    ####################

    def callback_on_help(self, update: Update, context: CallbackContext) -> None:  # pragma: no cover
        update.message.reply_text(available_commands_msg)

    def callback_on_start(self, update: Update, context: CallbackContext) -> None:  # pragma: no cover
        chat_id = update.effective_message.chat.id
        # check if user already has levels assigned
        levels = self.dao.get_user_levels(chat_id)
        user_levels = levels if levels else list(utils.POSSIBLE_USER_LEVELS)

        message = update.message or update.callback_query.message
        self.dao.save_user(message, user_levels)

        msg = f"Hello {message.chat.first_name}! " + available_commands_msg
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("/stop", callback_data='/stop')]
        ])

        if update.callback_query:
            update.callback_query.answer()
            update.callback_query.edit_message_text(msg, reply_markup=reply_markup)
        else:
            update.effective_message.reply_text(msg, reply_markup=reply_markup)

    def callback_on_stop(self, update: Update, context: CallbackContext) -> None:  # pragma: no cover
        chat_id = update.effective_message.chat.id
        self.dao.set_user_inactive(chat_id)

        msg = "You will no longer receive words!\n...Unles you use /start"
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("/start", callback_data='/start')]
        ])

        if update.callback_query:
            update.callback_query.answer()
            update.callback_query.edit_message_text(msg, reply_markup=reply_markup)
        else:
            update.effective_message.reply_text(msg, reply_markup=reply_markup)

    def callback_on_mylevels(self, update: Update, context: CallbackContext) -> None:  # pragma: no cover
        # get user information from the message
        chat_id = update.effective_message.chat_id

        # look for the levels of the user in the db
        levels = self.dao.get_user_levels(chat_id)

        # generate answer message and the markup
        answer = utils.build_levels_answer(levels)
        msg, reply_markup = answer.get('msg'), answer.get('reply_markup')

        # answer the user
        if update.callback_query:
            update.callback_query.answer()
            update.callback_query.edit_message_text(msg, reply_markup=reply_markup)
        else:
            update.effective_message.reply_text(msg, reply_markup=reply_markup)

    def callback_on_removelevel(self, update: Update, context: CallbackContext) -> None:  # pragma: no cover
        # get user information from the message
        chat_id = update.effective_message.chat.id

        callback_data = update.callback_query.data.split(" ")
        level = " ".join(callback_data[1:])

        # remove level from the user
        self.dao.remove_user_level(chat_id, level)

        # show user levels
        self.callback_on_mylevels(update, context)

    def callback_on_addlevel(self, update: Update, context: CallbackContext) -> None:  # pragma: no cover
        # get user information from the message
        chat_id = update.effective_message.chat.id

        callback_data = update.callback_query.data.split(" ")
        level = " ".join(callback_data[1:])

        # add level to the user
        self.dao.add_user_level(chat_id, level)

        # show user levels
        self.callback_on_mylevels(update, context)

    def callback_on_info(self, update: Update, context: CallbackContext) -> None:  # pragma: no cover
        msg = f"""Version: <i>{config.VERSION}</i> deployed on {self.start_date}
        \nWord bank info:\n - {len(self.word_bank.df.index)} words, last updated on {self.word_bank.last_updated_at}"""
        update.message.reply_text(msg, parse_mode='HTML')

    def callback_on_get_blockwords_callback(self, update: Update, context: CallbackContext) -> None:  # pragma: no cover

        chat_id = update.effective_message.chat.id

        blocked_word_ids = self.dao.get_user_blocked_words(chat_id)
        blocked_words = self.word_bank.get_words(blocked_word_ids)

        inline_keyboard_buttons = []

        for blocked_word in blocked_words:
            word_id = blocked_word["word_id"]
            german_word = blocked_word["de"]
            spanish_word = blocked_word["es"]
            spanish_and_german_word = "🇪🇸" + spanish_word + " | " + "🇩🇪" + german_word
            inline_keyboard_buttons.append([InlineKeyboardButton(spanish_and_german_word, callback_data=f'/unblockword_fbw {word_id}')])

        reply_markup = InlineKeyboardMarkup(inline_keyboard_buttons)

        msg = "These are your blocked words. Click to unblock them." if inline_keyboard_buttons else "You don't have any blocked words."

        if update.callback_query:
            update.callback_query.edit_message_text(msg, reply_markup=reply_markup)
        else:
            update.message.reply_text(msg, reply_markup=reply_markup)

    def callback_on_blockword(self, update: Update, context: CallbackContext):  # pragma: no cover
        update.callback_query.answer()
        callback_data = update.callback_query.data.split(" ")
        word_id = " ".join(callback_data[1:])

        self.dao.save_user_blocked_word(update.callback_query.message, word_id)
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Zurücknehmen - Deshacer", callback_data=f"/unblockword {word_id}")]
        ])
        msg = "✅\n" + update.callback_query.message.text
        update.callback_query.edit_message_text(msg, reply_markup=reply_markup)
        update.callback_query.answer()

    def callback_on_unblockword(self, update: Update, context: CallbackContext, is_from_blocked_words=False):  # pragma: no cover
        """Arg is_from_blocked_words indicates whether it was called from the /blockedwords comand. If so,
        it should show the updated /blockedwords output"""

        update.callback_query.answer()
        callback_data = update.callback_query.data.split(" ")
        word_id = " ".join(callback_data[1:])

        self.dao.remove_user_blocked_word(update.callback_query.message, word_id)

        # if called from blocked words, should show the updated blocked words
        if is_from_blocked_words:
            return self.callback_on_get_blockwords_callback(update, context)
        else:
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Gelernt! - Aprendida!", callback_data=f"/blockword {word_id}")]
            ])
            msg = update.callback_query.message.text[2:]  # remove '✅\n'
            update.callback_query.edit_message_text(msg, reply_markup=reply_markup)

    def callback_on_cancel(self, update: Update, context: CallbackContext) -> None:  # pragma: no cover
        update.callback_query and update.callback_query.answer()
        msg = "Cancelled."
        update.effective_message.reply_text(msg)
        return ConversationHandler.END

    # Admin Callbacks

    @admin_only
    def callback_on_users(self, update: Update, context: CallbackContext) -> None:  # pragma: no cover
        users = list(self.dao.get_all_users())
        msg = utils.build_users_msg(users)
        update.message.reply_text(msg)

    @admin_only
    def callback_on_broadcast(self, update: Update, context: CallbackContext) -> None:  # pragma: no cover
        msg = "Type the message you wanna broadcast:"
        update.effective_message.reply_text(msg, reply_markup=InlineKeyboardMarkup(Buttons.cancel))
        return States.BROADCAST_TYPE

    @admin_only
    def callback_on_broadcast_confirm(self, update: Update, context: CallbackContext) -> None:  # pragma: no cover
        msg = utils.build_broadcast_preview_msg(update.message.text)
        update.effective_message.reply_text(msg, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Send", callback_data="/broadcast_send"), (Buttons.cancel[0][0])]]
        ))
        return States.BROADCAST_CONFIRM

    @admin_only
    def callback_on_broadcast_send(self, update: Update, context: CallbackContext) -> None:  # pragma: no cover
        update.callback_query.answer()
        msg = utils.get_broadcast_msg_from_preview(update.callback_query.message.text)
        users = self.dao.get_all_active_users()
        for user in users:
            self.send_message_to_user(user, msg)
        return ConversationHandler.END

    ####################
    # Job Callbacks    #
    ####################

    def job_callback_send_word(self, context: CallbackContext):  # pragma: no cover
        users = self.dao.get_all_active_users()
        logger.info(f"sending words to {len(users)} users")

        for user in users:
            self.send_user_word(user)

    ####################
    # Core Stuff       #
    ####################

    @handle_error_send_user
    def send_message_to_user(self, user: dict, msg: str, reply_markup=None):
        chat_id = user["chatId"]
        self.updater.bot.send_message(chat_id=chat_id, text=msg, reply_markup=reply_markup, parse_mode='HTML')

    @handle_error_send_user
    def send_user_word(self, user: dict):  # pragma: no cover
        chat_id = user["chatId"]
        exclude = self.dao.get_user_blocked_words(chat_id)
        levels = self.dao.get_user_levels(chat_id)
        word_data = self.word_bank.get_random(levels, exclude=exclude)

        if word_data:
            msg = utils.build_word_msg(word_data)
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Gelernt! - ¡Aprendida!", callback_data=f"/blockword {word_data['word_id']}")]
            ])
        else:
            msg = 'Du hast alles gelernt! - ¡Te lo has aprendido todo!'
            reply_markup = None

        self.send_message_to_user(user, msg, reply_markup=reply_markup)

    def send_message_to_admins(self, msg: str):  # pragma: no cover
        for chat_id in config.ADMIN_CHAT_IDS:
            self.updater.bot.send_message(chat_id=chat_id, text=msg, parse_mode='HTML')

    @staticmethod
    def is_admin(chat_id: str):
        return str(chat_id) in config.ADMIN_CHAT_IDS

    def error_handler(self, update: object, context: CallbackContext) -> None:  # pragma: no cover
        """Send error msg to admins"""
        logger.error(msg="Exception while handling an update:", exc_info=context.error)

        traceback_str = ''.join(traceback.format_exception(None, context.error, context.error.__traceback__))

        user_str = ""
        if update:
            chat_id = update.effective_message.chat.id
            first_name = update.effective_message.chat.first_name
            user_str = f"Happened to user: {chat_id} - {first_name}"
        msg = (
            f'An exception was raised while handling an update. {user_str}\n\n'
            f'<pre>{html.escape(traceback_str)}</pre>'
        )

        self.send_message_to_admins(msg)

    def __init__(self):
        self.start_date = datetime.now()
        self.dao = DAO(config.REDIS_HOST)
        self.word_bank = WordBank(config.WORD_BANK_LOCAL)
        self.backup_service = BackupService()

    def run(self):  # pragma: no cover
        """Run bot"""
        logger.info("Started app")

        self.updater = Updater(config.BOT_TOKEN)
        self.updater.bot.set_my_commands(user_bot_commands)

        self.updater.job_queue.run_custom(self.job_callback_send_word, job_kwargs=dict(
            trigger="cron",
            day="*",
            # hour="10,18,20",
            # minute="30",
            second="10,20,30,40,50,0"  # test
        ))
        self.updater.job_queue.run_custom(lambda x: self.word_bank.update(), job_kwargs=dict(
            trigger="cron",
            day="*",
            hour="7",
            # second="10,20,30,40,50,0"  # test
        ))

        # Bot conversation flow logic
        broadcast_handler = ConversationHandler(
            entry_points=[
                CommandHandler("start", self.callback_on_start),
                CallbackQueryHandler(self.callback_on_start, pattern=r"\/start"),

                CommandHandler("stop", self.callback_on_stop),
                CallbackQueryHandler(self.callback_on_stop, pattern=r"\/stop"),

                CommandHandler("blockedwords", self.callback_on_get_blockwords_callback),
                CallbackQueryHandler(self.callback_on_blockword, pattern=r"\/blockword .*"),
                CallbackQueryHandler(self.callback_on_unblockword, pattern=r"\/unblockword .*"),
                # fbw = from blocked words
                CallbackQueryHandler(lambda u, c: self.callback_on_unblockword(u, c, is_from_blocked_words=True), pattern=r"\/unblockword_fbw .*"),

                CommandHandler("mylevels", self.callback_on_mylevels),
                CallbackQueryHandler(self.callback_on_addlevel, pattern=r"\/addlevel .*"),
                CallbackQueryHandler(self.callback_on_removelevel, pattern=r"\/removelevel .*"),

                CommandHandler("help", self.callback_on_help),
                CommandHandler("info", self.callback_on_info),
                # admin
                CommandHandler("users", self.callback_on_users),
                CommandHandler("broadcast", self.callback_on_broadcast),
            ],
            states={
                States.BROADCAST_TYPE: [
                    MessageHandler(Filters.regex("^(?!/).*"), self.callback_on_broadcast_confirm)
                ],
                States.BROADCAST_CONFIRM: [
                    CallbackQueryHandler(self.callback_on_broadcast_send, pattern=r"\/broadcast_send")
                ],
            },
            fallbacks=[
                CommandHandler("cancel", self.callback_on_cancel),
                CallbackQueryHandler(self.callback_on_cancel, pattern=r"\/cancel")
            ],
        )

        self.updater.dispatcher.add_handler(broadcast_handler)
        self.updater.dispatcher.add_error_handler(self.error_handler)

        self.updater.start_polling()
        self.updater.idle()
