from django.core.management.base import BaseCommand
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, \
    CallbackQueryHandler
from telegram.utils.request import Request
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
import logging
import qrcode
from PIL import Image
from io import BytesIO
from main.models import Review, Place

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

FEEDBACK, PHOTO, LOCATION = range(3)


# simple error handler
def log_errors(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error_message = f'Exception!! {e}'
            print(error_message)
            raise e

    return inner


'''
@log_errors
def handle_message(update : Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text

    reply_text = f'Chat id = {chat_id}\n\n message = {text}'
    update.message.reply_text(text = reply_text)
'''


def start(update: Update, _: CallbackContext) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Оставить отзыв", callback_data='1'),
            InlineKeyboardButton("Почитать отзывы", callback_data='2'),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Привет, я бот который поможет оставить отзыв о благоустроенной территории. '
                              'Выбери что хочешь сделать: Набери /cancel чтобы перестать со мной общаться\n\n',
                              reply_markup=reply_markup)


def help_command(update: Update, _: CallbackContext) -> None:
    update.message.reply_text("Пожалуйста, выберите что вы хотите сделать нажав start")


def create_qr_code(place_name, bot_name):
    img = qrcode.make(f'https://t.me/{bot_name}/start={place_name}')
    bio = BytesIO()
    bio.name = 'image.jpeg'
    img.save(bio, 'JPEG')
    bio.seek(0)
    return bio


def feedback(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Get feedback of %s: %s", user.first_name, update.message.text)
    p, _ = Place.objects.get_or_create(id=1)
    Review.objects.create(
        place=p,
        text=update.message.text,
        author='Anonymuos',
        author_id=update.message.chat_id,
    )
    update.message.reply_text(
        'Отлично. Теперь отправьте мне пожалуйста фото территории, '
        f'или нажмите /skip чтобы пропустить, {user.name}',
        reply_markup=ReplyKeyboardRemove(),
    )

    return PHOTO


def button(update: Update, _: CallbackContext) -> int:
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    query.edit_message_text(text=f"Selected option: {query.data}")
    if query.data == '2':
        query.edit_message_text(text=f"Пока этот раздел не доступен в демо версии бота."
                                     f" Возможно он появится позже, и Вы сможете читать комментарии"
                                     f" Нажмите /start чтобы начать сначала или /cancel")
    if query.data == '1':
        query.edit_message_text(text=f"Отлично. Напишите пожалуйста полный текст отзыва о благоустроенной территории.\n"
                                     f" Нажмите /start чтобы начать сначала или /cancel чтобы закончи ть разговор")
        return FEEDBACK


def photo(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text(
        'Отлично! Теперь отправьте мне пожалуйста свое местоположение или нажмите /skip для того чтобы пропустить'
    )

    return LOCATION


def skip_photo(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text(
        'Что ж,,отправьте мне тогда пожалуйста свое местоположение или нажмите /skip для того чтобы пропустить'
    )

    return LOCATION


def location(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    user_location = update.message.location
    logger.info(
        "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
    )
    update.message.reply_text(
        'Ок. Я принял отзыв. Спасибо за потраченно время.'
    )

    return ConversationHandler.END


def skip_location(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    update.message.reply_text(
        'Хорошо, будем работать с тем что есть) Я принял отзыв. Спасибо за потраченно время. '
    )

    return ConversationHandler.END


def cancel(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Хорошо, попробуем пообщаться в другой раз', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


class Command(BaseCommand):
    help = 'Telegram-bot'

    def handle(self, *args, **options):
        request = Request(connect_timeout=0.5, read_timeout=1.0)

        # reading telegram token
        f = open('token.txt')
        token = f.read()

        updater = Updater(token)

        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher
        # начало работы бота, начинаем с команды /start
        updater.dispatcher.add_handler(CommandHandler('start', start))
        updater.dispatcher.add_handler(CallbackQueryHandler(button))
        updater.dispatcher.add_handler(CommandHandler('help', help_command))
        # Add conversation handler with the states FEEDBACK, PHOTO, LOCATION
        conv_handler = ConversationHandler(
            entry_points=[MessageHandler(Filters.text & ~Filters.command, feedback)],
            states={
                FEEDBACK: [MessageHandler(Filters.text & ~Filters.command, feedback)],
                PHOTO: [MessageHandler(Filters.photo, photo), CommandHandler('skip', skip_photo)],
                LOCATION: [
                    MessageHandler(Filters.location, location),
                    CommandHandler('skip', skip_location),
                ]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )

        dispatcher.add_handler(conv_handler)

        # creating the bot
        # bot = telegram.Bot(token=token, request=request)

        # run this to see bot parameters
        # print(bot.get_me())

        # updater = Updater(token=token, use_context=True)
        # message_handler = MessageHandler(Filters.text, handle_message)
        # updater.dispatcher.add_handler(message_handler)

        updater.start_polling()
        updater.idle()
