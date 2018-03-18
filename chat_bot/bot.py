import sqlite3
import requests
import utilities.messages as msg
from telegram.ext import RegexHandler
from telegram.ext import run_async
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from chat_bot.DbOperator import DbOperator


class Bot():
    def __init__(self, translate_url, translate_token, bot_token, db_address):
        self.db_address = db_address
        self.translate_url = translate_url
        self.translate_token = translate_token
        self.bot_token = bot_token
        self.__db_connect()
        self.__create_updater(self.bot_token)

    def __db_connect(self):
        connection = DbOperator.connect(self.db_address)
        try:
            DbOperator.create(connection)
            DbOperator.disconnect(connection)
        except sqlite3.OperationalError:
            DbOperator.disconnect(connection)

    def __create_updater(self, token):
        updater = Updater(token)
        updater.dispatcher.add_handler(CommandHandler('lang', self.lang))
        updater.dispatcher.add_handler(CommandHandler('start', self.start))
        updater.dispatcher.add_handler(CallbackQueryHandler(self.button))
        updater.dispatcher.add_handler(CommandHandler('help', self.help))
        updater.dispatcher.add_handler(CommandHandler('tr', self.translation))
        updater.dispatcher.add_handler(CommandHandler('look', self.look_lang))
        updater.dispatcher.add_handler(MessageHandler(Filters.text, self.__text_handler))
        updater.dispatcher.add_handler(RegexHandler(r'/.*', self.__unknown_cmd))
        print(msg.startup_info)
        updater.start_polling()
        updater.idle()

    def look_lang(self, bot, update):
        connection = DbOperator.connect(self.db_address)
        cursor = DbOperator.get_cursor(connection)
        row = DbOperator.select(cursor, update.message.chat_id)
        if row is None:
            update.message.reply_text('Настройки языка ещё не установлены. '
                                      'Пожалуйста, выберите язык перевода, набрав команду: /lang')
        else:
            update.message.reply_text("Выбрано направление перевода: {}".format(row[1]))
        DbOperator.disconnect(connection)

    def help(self, bot, update):
        update.message.reply_text(msg.help_msg)

    def __unknown_cmd(self, bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text=msg.undefined_cmd_msg)

    def __text_handler(self, bot, update):
        update.message.reply_text(msg.text_handle_msg)

    def lang(self, bot, update):
        keyboard = [[InlineKeyboardButton("Русский-Английский", callback_data='ru-en'),
                     InlineKeyboardButton("Английский-Русский", callback_data='en-ru')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Выберите напрвление перевода:', reply_markup=reply_markup)

    def start(self, bot, update):
        update.message.reply_text(msg.start_msg)

    @run_async
    def __add_user(self, chat_id, language):
        connection = DbOperator.connect(self.db_address)
        cursor = DbOperator.get_cursor(connection)

        row = DbOperator.select(cursor, chat_id)
        if row is not None:
            DbOperator.update(cursor, chat_id, language)
            DbOperator.disconnect(connection)
        else:
            DbOperator.insert(cursor, chat_id, language)
            DbOperator.disconnect(connection)

    @run_async
    def button(self, bot, update):
        chat_id = update.callback_query.message.chat_id
        selected_lang = update.callback_query.data
        self.__add_user(chat_id, selected_lang)
        bot.edit_message_text(text="Напрвление перевода: {}".format(selected_lang),
                              chat_id=update.callback_query.message.chat_id,
                              message_id=update.callback_query.message.message_id)

    @run_async
    def translation(self, bot, update):
        text = update.message.text[4:]
        if text == '':
            update.message.reply_text('Текст после команды /tr отсутствует')
        else:
            connection = DbOperator.connect(self.db_address)
            cursor = DbOperator.get_cursor(connection)
            row = DbOperator.select(cursor, update.message.chat_id)
            if row is None:
                update.message.reply_text('Пожалуйста, выберите язык перевода, набрав команду: /lang')
            else:
                translation_text = self.__do_request(row[1], text)
                update.message.reply_text(translation_text)
            DbOperator.disconnect(connection)

    def __do_request(self, lang_set, text_for_translation):
        r = requests.get(self.translate_url, data={'key': self.translate_token, 'text': text_for_translation,
                                                   'lang': lang_set})
        translate_text = (r.json())['text'][0]
        return translate_text