from django.core.management.base import BaseCommand
import telegram
from statsmodels.compat import numpy
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, \
    CallbackQueryHandler
from telegram.utils.request import Request
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, Bot
import logging
import qrcode
from PIL import Image
from io import BytesIO
from main.models import Review, Place, SuperUser

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

FEEDBACK, PHOTO, LOCATION, ADMIN, START, FIND_PLACE_TO_REVIEW, SHOW_REVIEWS = range(7)
_place = ''


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


@log_errors
def handle_message(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text

    reply_text = f'Chat id = {chat_id}\n\n message = {text}'
    update.message.reply_text(text=reply_text)


def start(update: Update, callback: CallbackContext) -> None:
    user = update.message.from_user
    # superuser = bool(SuperUser.objects.filter(username=user.username))
    superuser = True
    if not superuser and not callback.args:
        user_text = 'Привет, я бот который поможет оставить отзыв о благоустроенной территории. ' + \
                    'Напиши название места, о котором ты хочешь оставить отзыв.' + \
                    ' Набери /cancel чтобы перестать со мной общаться\n\n'

        update.message.reply_text(user_text)
        return FIND_PLACE_TO_REVIEW
    text = ''
    keyboard = None
    if not superuser:
        text = f'Привет, я бот который поможет оставить отзыв о благоустроенной территории. ' + \
                    f'Ты хочешь оставить отзыв оюб этом месте: {callback.args}, верно?'
        keyboard = [
            [
                InlineKeyboardButton("Да", callback_data='4'),
                InlineKeyboardButton("Нет", callback_data='5'),
            ],
        ]
    else:
        keyboard = [
            [
                InlineKeyboardButton("Оставить отзыв", callback_data='1'),
                InlineKeyboardButton("Почитать отзывы", callback_data='2'),
            ],
            [InlineKeyboardButton("Добавить место", callback_data='3')],
        ]
        text = 'Привет, я бот который поможет оставить отзыв о благоустроенной территории.\n ' + \
                     'Выбери что хочешь сделать: Набери /cancel чтобы перестать со мной общаться\n\n' + \
                     'Для Вас доступна панель Админа. Можете добавить место самостоятельно!\n\n'
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text, reply_markup=reply_markup)


def find_place_to_review(update: Update, context: CallbackContext):
    place = Place.objects.filter(name=update.message.text.upper()).last()
    if place:
        update.message.reply_text(text=f"Отлично. Напишите пожалуйста полный текст отзыва о благоустроенной "
                                       f"территории.\n Нажмите /start чтобы начать сначала или /cancel чтобы закончи "
                                       f"ть разговор")
        global _place
        _place = place
        return FEEDBACK
    update.message.reply_text(text=f"Извините, не знаю такого места. Поробуйте еще раз"
                                   f"\n Нажмите /start чтобы начать сначала или /cancel чтобы закончи "
                                   f"ть разговор")
    return FIND_PLACE_TO_REVIEW


def help_command(update: Update, _: CallbackContext) -> None:
    update.message.reply_text("Пожалуйста, выберите что вы хотите сделать нажав start")


def feedback(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Get feedback of %s: %s", user.first_name, update.message.text)

    p = Place.objects.get(name=_place)
    if p:
        Review.objects.create(
            place=p,
            text=update.message.text,
            author=user.full_name,
            author_id=update.message.chat_id,
        )
        update.message.reply_text(
            'Отлично. Теперь отправьте мне пожалуйста фото территории, '
            f'или нажмите /skip чтобы пропустить, {user.full_name}',
            reply_markup=ReplyKeyboardRemove())
        return PHOTO
    else:
        update.message.reply_text(
            'Извините, не знаю такого меса',
            reply_markup=ReplyKeyboardRemove())
        update.message.reply_text('Можете нажать /start чтобы начать с начала')
        return ConversationHandler.END


def button(update: Update, _: CallbackContext) -> int:
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    query.edit_message_text(text=f"Selected option: {query.data}")
    if query.data == '2':
        query.edit_message_text(text=f"Напишите название места, о котором хотите почитать отзывы.")
        return SHOW_REVIEWS
    elif query.data == '1' or query.data == '5':
        query.edit_message_text(
            text='Напишите название места, о котором вы хотите оставить отзыв.' + \
                 ' Набери /cancel чтобы перестать со мной общаться\n\n')
        return FIND_PLACE_TO_REVIEW
    elif query.data == '3':
        query.edit_message_text(
            text=f"Ok. Вы админ и вы хотите добавить место. Напишите название вашего места\n"
                 f" Нажмите /start чтобы начать сначала или /cancel чтобы закончить разговор")
        return ADMIN
    elif query.data == '4':
        return FEEDBACK


def admin_add_place(update: Update, context: CallbackContext) -> int:
    place_name = update.message.text.upper()
    user = update.message.from_user
    logger.info("Get place from ADMIN %s: %s", user.first_name, update.message.text)
    print("into admin function")
    Place.objects.create(name=place_name)
    update.message.reply_text(text=f"Отлично. Название пришло, добавляю, {update.message.text}. \n Вот QR-код, "
                                   f"который нужно будет повесить на стенде: ")
    img = create_qr_code(f'https://t.me/{context.bot.name[1:]}', place_name)
    context.bot.sendPhoto(update.message.chat_id, img)
    update.message.reply_text(text=f"Можете вернуться и оставить отзыв, или прочитать. Нажмите /start",
                              reply_markup=ReplyKeyboardRemove(),
                              )
    return ConversationHandler.END


def create_qr_code(invite_link, place_name):
    img = qrcode.make(f'{invite_link}?start={place_name}')
    bio = BytesIO()
    bio.name = 'image.jpeg'
    img.save(bio, 'JPEG')
    bio.seek(0)
    return bio


def photo(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    photo_file = update.message.photo[-1].get_file()
    bio = BytesIO()
    photo_file.download(out=bio)
    bio.seek(0)
    img = Image.open(bio)

    bio2 = BytesIO()
    bio2.name = 'image.jpg'
    img.save(bio2, optimize=True, quality=30)
    bio2.seek(0)

    r = Review.objects.filter(author_id=update.message.chat_id).last()
    img = Image.open(bio2)
    r.photo = img.tobytes()
    r.photo_height = img.height
    r.photo_width = img.width

    r.save(update_fields=['photo', 'photo_height', 'photo_width'])

    update.message.reply_text('Ок. Я принял отзыв. Спасибо за потраченно время.')
    update.message.reply_text('Можете нажать /start чтобы начать с начала')

    return ConversationHandler.END


def skip_photo(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text(
        'Ок. Я принял отзыв. Спасибо за потраченно время.'
    )
    update.message.reply_text('Можете нажать /start чтобы начать с начала')

    return ConversationHandler.END


def cancel(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Хорошо, попробуем пообщаться в другой раз', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def show_reviews(update: Update, context: CallbackContext):
    place_name = update.message.text.upper()
    p = Place.objects.filter(name=place_name).last()
    if p:
        for review in Review.objects.filter(place=p).iterator():
            # if review.photo:
            update.message.reply_text(f'-'*100)
            update.message.reply_text(f'Автор: {review.author}')
            update.message.reply_text(f'\n\nТекст: {review.text}')
            if review.photo:
                width = review.photo_width if review.photo_width is not None else 1280
                height = review.photo_height if review.photo_height is not None else 1280
                img = Image.frombytes('RGB', (width, height), review.photo)
                bio = BytesIO()
                bio.name = 'image.jpg'
                img.save(bio)
                bio.seek(0)
                context.bot.sendPhoto(update.message.chat_id, bio)
    else:
        update.message.reply_text(
            f'Не вижу отзывов об этом метсе'
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
        # updater.dispatcher.add_handler(CommandHandler('start', start))
        # updater.dispatcher.add_handler(CallbackQueryHandler(button))
        updater.dispatcher.add_handler(CommandHandler('help', help_command))
        # Add conversation handler with the states FEEDBACK, PHOTO, LOCATION
        conv_handler = ConversationHandler(
            entry_points=[(CommandHandler('start', start, pass_user_data=True, pass_chat_data=True)),
                          CallbackQueryHandler(button, pass_user_data=True, pass_chat_data=True)],
            states={
                ADMIN: [MessageHandler(Filters.text, admin_add_place)],
                FEEDBACK: [MessageHandler(Filters.text & ~Filters.command, feedback, pass_user_data=True, pass_chat_data=True)],
                PHOTO: [MessageHandler(Filters.photo, photo), CommandHandler('skip', skip_photo)],
                FIND_PLACE_TO_REVIEW: [
                    MessageHandler(Filters.text & ~Filters.command, find_place_to_review, pass_user_data=True, pass_chat_data=True)],
                SHOW_REVIEWS: [MessageHandler(Filters.text & ~Filters.command, show_reviews, pass_user_data=True, pass_chat_data=True)],
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
