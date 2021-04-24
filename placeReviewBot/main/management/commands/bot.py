from django.core.management.base import BaseCommand
import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.utils.request import Request
from telegram.ext import MessageHandler, Filters, CallbackContext
from telegram import Update


#simple error handler
def log_errors(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error_message = f'Exception!! {e}'
            print(error_message)
            raise e
    return inner


@log_errors
def handle_message(update : Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text

    reply_text = f'Chat id = {chat_id}\n\n message = {text}'
    update.message.reply_text(text = reply_text)


class Command(BaseCommand):
    help = 'Telegram-bot'

    def handle(self, *args, **options):
        request = Request(connect_timeout=0.5, read_timeout=1.0)

        # reading telegram token
        f = open('token.txt')
        token = f.read()

        # creating the bot
        bot = telegram.Bot(token=token, request=request)

        # run this to see bot parameters
        # print(bot.get_me())

        updater = Updater(token=token, use_context=True)
        message_handler = MessageHandler(Filters.text, handle_message)
        updater.dispatcher.add_handler(message_handler)

        updater.start_polling()
        updater.idle()
