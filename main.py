import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler


# reading telegram token
f = open('token.txt')
token = f.read()

# creating the bot
bot = telegram.Bot(token=token)


# run this to see bot parameters
# print(bot.get_me())


updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a vsratiy bot!!! "
                                                                    "You can past your feedback here! Type and CRY!")


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.start_polling()