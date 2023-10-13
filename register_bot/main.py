import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler, \
    CallbackContext

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

START, COURSE_SELECTION, NAME, PHONE, ADMIN, NEW_REGISTRATION = range(6)

user_data = {}
registered_users = []
admin_password = 'ADMIN-PASSWORD'
admin_chat_id = 'ADMIN-CHAT-ID'
bot_token = 'TELEGRAM-BOT-TOKEN'


def start(update: Update, context: CallbackContext):
    user = update.effective_user
    context.user_data.clear()
    keyboard = [[KeyboardButton("Ingliz tili")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    update.message.reply_text(
        f"Salom {user.mention_html()} !\n\n"
        "<b>Kursni tanlang</b>:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

    return COURSE_SELECTION


def course_selection(update: Update, context: CallbackContext):
    text = update.message.text
    context.user_data['course'] = text
    update.message.reply_text(
        f"👩🏻‍💻 Siz quydagi kursni tanladingiz: <b>{text}</b>\n\n"
        f"Iltimos, <b>Ism Familyangizni</b> to'liq va bexato kiriting :",
        parse_mode='HTML', reply_markup=ReplyKeyboardRemove()
    )

    return NAME


def name(update: Update, context: CallbackContext):
    if 'course' not in context.user_data:
        update.message.reply_text("Kursni tanlamaganingiz uchun xatolik yuz berdi. /start buyrug'ini qayta bosing.")
        return ConversationHandler.END

    context.user_data['name'] = update.message.text

    keyboard = [[KeyboardButton("Raqamni yuborish", request_contact=True)]]

    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    update.message.reply_text(
        "Iltimos, <b>Telefon raqamingiz</b>ni kiriting :",
        reply_markup=reply_markup, parse_mode='HTML',
    )

    return PHONE


def phone(update: Update, context: CallbackContext):
    if 'name' not in context.user_data:
        update.message.reply_text("Ismingizni kiritmaganingiz uchun xatolik yuz berdi. /start buyrug'ini qaytadan "
                                  "bosing.")
        return ConversationHandler.END

    context.user_data['phone'] = update.message.contact.phone_number
    registration_message = (
        f"<b>Roʻyxatdan oʻtish tugallandi 🥳</b>\n\n"
        f"<b>Kurs</b>: {context.user_data['course']}\n"
        f"<b>Ism</b>: {context.user_data['name']}\n"
        f"<b>Telefon</b>: {context.user_data['phone']}\n\n Tez orada siz bilan bog'lanishadi, agar 1-2 kun ichida "
        f"javob kelmasa <b>(Ma'lumotni o'chirish)</b> dan foydalanib, qayta kiritishingiz mumkin !"
    )
    registered_users.append(context.user_data.copy())
    keyboard = [[InlineKeyboardButton("Ma'lumotni o'chirish", callback_data=f"remove_{len(registered_users) - 1}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(registration_message, reply_markup=reply_markup, parse_mode='HTML')
    context.user_data.clear()

    return ConversationHandler.END


def remove_user(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    index = int(query.data.split('_')[1])

    if 0 <= index < len(registered_users):
        removed_user = registered_users.pop(index)
        query.edit_message_text(f"Ma'lumotingiz Admindan olib tashlandi ! Botdan qayta foydalanish uchun 👉 /start "
                                f"dan foydalaning !\n\n"
                                f"Kurs: {removed_user.get('course', 'Kursi yoq')}\n"
                                f"Ism: {removed_user.get('name', 'Nomi yoq')}\n"
                                f"Telefon: {removed_user.get('phone', 'Telefon raqami yoq')}", parse_mode='HTML')

    else:
        query.edit_message_text("Ma'lumotingiz Admindan olib tashlandi ! Botdan qayta foydalanish uchun 👉 /start "
                                f"dan foydalaning !", parse_mode='HTML')


def admin(update: Update, context: CallbackContext):
    entered_password = update.message.text
    if entered_password[7:] == admin_password:
        if registered_users:
            for index, user in enumerate(registered_users):
                user_info = (f"<b>Ro'xatdan o'tgan foydalanuvchi :</b>\n\n"
                             f"<b>Kursi</b>: {user.get('course', 'Kurs ni kiritmagan')}\n"
                             f"<b>Ismi</b>: {user.get('name', 'Ism Familya kiritmagan')}\n"
                             f"<b>Telefon raqami</b>: {user.get('phone', 'Telefon raqam kiritmagan')}"
                             )
                keyboard = [[InlineKeyboardButton("Ma'lumotni o'chirish", callback_data=f"remove_{index}")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text(user_info, reply_markup=reply_markup, parse_mode='HTML')
        else:
            update.message.reply_text("Hozircha ro'yxatdan o'tgan foydalanuvchilar yo'q 😕")
        return ConversationHandler.END
    else:
        update.message.reply_text("Admin paroli noto'g'ri !")


def new_registration(update: Update, context: CallbackContext):
    keyboard = [[KeyboardButton("Ingliz tili")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    update.message.reply_text(
        "Assalomu Alaykum, qaysi kursni tanlashni xohlaysiz ?",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

    return COURSE_SELECTION


def main():
    updater = Updater(token=bot_token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CallbackQueryHandler(remove_user, pattern=r'^remove_\d+$'))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), CommandHandler('new_registration', new_registration)],
        states={
            COURSE_SELECTION: [MessageHandler(Filters.text & ~Filters.command, course_selection)],
            NAME: [MessageHandler(Filters.text & ~Filters.command, name)],
            PHONE: [MessageHandler(Filters.contact, phone)],  # Use Filters.contact to capture the phone number
            ADMIN: [MessageHandler(Filters.text & ~Filters.command, admin)]
        },
        fallbacks=[]
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler('admin', admin))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
