import typing
import logging
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

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


class App:

    def callback_on_info(self, update: Update, context: CallbackContext) -> None:  # pragma: no cover
        msg = f"Version: {config.VERSION} deployed on {self.start_date}"
        update.message.reply_text(msg)

    def on_help_callback(self, update: Update, context: CallbackContext) -> None:  # pragma: no cover
        update.message.reply_text(available_commands_msg)

    def on_users_callback(self, update: Update, context: CallbackContext) -> None:  # pragma: no cover
        if str(update.message.chat_id) == config.ADMIN_CHAT_ID:
            users = list(self.dao.get_all_users())
            msg = utils.build_users_msg(users)
        else:
            msg = "Loitering around my github?\nDon't hesitate greeting me! 😀"
        update.message.reply_text(msg)

    def on_start_callback(self, update: Update, context: CallbackContext, is_inline_keyboard=False) -> None:  # pragma: no cover
        message = update.message or update.callback_query.message
        chat_id = message.chat_id
        # check if user already has levels assigned
        levels = self.dao.get_user_levels(chat_id)
        user_levels = levels if levels else utils.POSSIBLE_USER_LEVELS
        self.dao.save_user(message, user_levels)

        msg = f"Hello {message.chat.first_name}! " + available_commands_msg
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("/stop", callback_data='/stop')]
        ])

        if is_inline_keyboard:
            update.callback_query.edit_message_text(msg, reply_markup=reply_markup)
        else:
            update.message.reply_text(msg, reply_markup=reply_markup)

    def on_stop_callback(self, update: Update, context: CallbackContext, is_inline_keyboard=False) -> None:  # pragma: no cover
        message = update.message or update.callback_query.message
        self.dao.set_user_inactive(message)

        msg = "You will no longer receive words!\n...Unles you use /start"
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("/start", callback_data='/start')]
        ])

        if is_inline_keyboard:
            update.callback_query.edit_message_text(msg, reply_markup=reply_markup)
        else:
            update.message.reply_text(msg, reply_markup=reply_markup)

    def on_get_blockwords_callback(self, update: Update, context: CallbackContext, is_inline_keyboard=False) -> None:  # pragma: no cover
        message = update.message or update.callback_query.message

        chat_id = message.chat_id

        blocked_word_ids = self.dao.get_user_blocked_words(chat_id)
        blocked_words = self.word_bank.get_words(blocked_word_ids)

        inline_keyboard_buttons = []

        for blocked_word in blocked_words:
            word_id = blocked_word["word_id"]
            german_word = blocked_word["de"]
            spanish_word = blocked_word["es"]
            spanish_and_german_word = "🇪🇸" + spanish_word + " | " + "🇩🇪" + german_word
            inline_keyboard_buttons.append([InlineKeyboardButton(spanish_and_german_word, callback_data=f'/unblockword_from_blocked_words {word_id}')])

        reply_markup = InlineKeyboardMarkup(inline_keyboard_buttons)

        msg = "These are your blocked words. Click to unblock them." if inline_keyboard_buttons else "You don't have any blocked words."

        if is_inline_keyboard:
            update.callback_query.edit_message_text(msg, reply_markup=reply_markup)
        else:
            update.message.reply_text(msg, reply_markup=reply_markup)

    def on_mylevels_callback(self, update: Update, context: CallbackContext, is_inline_keyboard=False) -> None:  # pragma: no cover
        # get user information from the message
        message = update.message or update.callback_query.message
        chat_id = message.chat_id

        # look for the levels of the user in the db
        levels = self.dao.get_user_levels(chat_id)

        # generate answer message and the markup
        answer = utils.build_levels_answer(levels)

        # answer the user
        if is_inline_keyboard:
            update.callback_query.edit_message_text(answer.get('msg'), reply_markup=answer.get('reply_markup'))
        else:
            update.message.reply_text(answer.get('msg'), reply_markup=answer.get('reply_markup'))

    def on_removelevel_callback(self, update: Update, context: CallbackContext, level_to_remove: str, is_inline_keyboard=False) -> None:  # pragma: no cover
        # get user information from the message
        message = update.message or update.callback_query.message
        chat_id = message.chat_id

        # remove level from the user
        self.dao.remove_user_level(chat_id, level_to_remove)

        # show user levels
        self.on_mylevels_callback(update, context, is_inline_keyboard)

    def on_addlevel_callback(self, update: Update, context: CallbackContext, level_to_add: str, is_inline_keyboard=False) -> None:  # pragma: no cover
        # get user information from the message
        message = update.message or update.callback_query.message
        chat_id = message.chat_id

        # add level to the user
        self.dao.add_user_level(chat_id, level_to_add)

        # show user levels
        self.on_mylevels_callback(update, context, is_inline_keyboard)

    def on_info_callback(self, update: Update, context: CallbackContext) -> None:  # pragma: no cover
        msg = f"""Version: <i>{config.VERSION}</i> deployed on {self.start_date}
        \nWord bank info:\n - {len(self.word_bank.df.index)} words, last updated on {self.word_bank.last_updated_at}"""
        update.message.reply_text(msg, parse_mode='HTML')

    def inline_keyboard_callbacks(self, update: Update, context: CallbackContext) -> None:  # pragma: no cover
        query = update.callback_query
        query.answer()

        callback_data = query.data.split(" ")
        command = callback_data[0]
        args = callback_data[1:]

        if command == "/start":
            self.on_start_callback(update, context, is_inline_keyboard=True)
        elif command == "/stop":
            self.on_stop_callback(update, context, is_inline_keyboard=True)
        elif command == "/blockword":
            word_id = args[0]
            self.dao.save_user_blocked_word(update.callback_query.message, word_id)
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Zurücknehmen - Deshacer", callback_data=f"/unblockword {word_id}")]
            ])
            msg = "✅\n" + update.callback_query.message.text
            update.callback_query.edit_message_text(msg, reply_markup=reply_markup)
        elif command == "/unblockword":
            word_id = args[0]
            self.dao.remove_user_blocked_word(update.callback_query.message, word_id)
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Gelernt! - Aprendida!", callback_data=f"/blockword {word_id}")]
            ])
            msg = update.callback_query.message.text[2:]  # remove '✅\n'
            update.callback_query.edit_message_text(msg, reply_markup=reply_markup)
        elif command == "/unblockword_from_blocked_words":
            word_id = args[0]
            self.dao.remove_user_blocked_word(update.callback_query.message, word_id)
            self.on_get_blockwords_callback(update, context, is_inline_keyboard=True)
        elif command == '/removelevel':
            level_to_remove = args[0]
            self.on_removelevel_callback(update, context, level_to_remove, is_inline_keyboard=True)
        elif command == '/addlevel':
            level_to_add = args[0]
            self.on_addlevel_callback(update, context, level_to_add, is_inline_keyboard=True)

    def send_word(self, context: CallbackContext):  # pragma: no cover
        users = self.dao.get_all_active_users()
        logger.info(f"sending words to {len(users)} users")

        for user in users:
            try:
                chat_id = user["chatId"]
                exclude = self.dao.get_user_blocked_words(chat_id)
                levels = self.dao.get_user_levels(chat_id)
                word_data = self.word_bank.get_random(exclude=exclude, levels=levels)

                msg: str = utils.build_word_msg(word_data) if word_data else 'Du hast alles gelernt! - ¡Te lo has aprendido todo!'

                reply_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("Gelernt! - ¡Aprendida!", callback_data=f"/blockword {word_data['word_id']}")]
                ])

                context.bot.send_message(chat_id=chat_id, text=msg, parse_mode='HTML', reply_markup=reply_markup)
            except Exception as e:
                logger.error("shit", exc_info=e)

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

        self.updater.job_queue.run_custom(self.send_word, job_kwargs=dict(
            trigger="cron",
            day="*",
            hour="10,18,20",
            minute="30",
            # second="10,20,30,40,50,0"  # test
        ))
        self.updater.job_queue.run_custom(lambda x: self.word_bank.update(), job_kwargs=dict(
            trigger="cron",
            day="*",
            hour="7",
            # second="10,20,30,40,50,0"  # test
        ))

        dispatcher = self.updater.dispatcher

        dispatcher.add_handler(CommandHandler("start", self.on_start_callback))
        dispatcher.add_handler(CommandHandler("stop", self.on_stop_callback))
        dispatcher.add_handler(CommandHandler("help", self.on_help_callback))
        dispatcher.add_handler(CommandHandler("users", self.on_users_callback))
        dispatcher.add_handler(CommandHandler("info", self.on_info_callback))
        dispatcher.add_handler(CommandHandler("blockedwords", self.on_get_blockwords_callback))
        dispatcher.add_handler(CommandHandler("mylevels", self.on_mylevels_callback))
        dispatcher.add_handler(CallbackQueryHandler(self.inline_keyboard_callbacks))

        self.updater.start_polling()
        self.updater.idle()
