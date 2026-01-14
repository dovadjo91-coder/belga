from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    BotCommand
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

TOKEN = "8352229914:AAFmGtsGXgylqrVmoYIIfq74iuTIp3N7GPQ"
ADMIN_ID = -1003609160995

NAME, TICKET, PHOTO, HELP = range(4)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🎯 Участвовать в розыгрыше"],
        ["📜 Правила", "📞 Контакты"],
        ["📍 Адрес", "ℹ️ О нас"],
        ["🌐 Наш сайт"]
    ]
    await update.message.reply_text(
        "👋 Добро пожаловать!\nВыберите команду ⬇️",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# Menu
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🎯 Участвовать в розыгрыше":
        await update.message.reply_text(
            "✍️ Введите ваше имя и номер:",
            reply_markup=ReplyKeyboardRemove()
        )
        return NAME

    elif text == "📜 Правила":
        await update.message.reply_text(
            "📜 Правила розыгрыша:\n"
            "1️⃣ Подпишитесь на канал\n"
            "2️⃣ Одна заявка на один билет\n"
            "3️⃣ Фото билета должно быть чётким"
        )

    elif text == "📞 Контакты":
        await update.message.reply_text(
            "📞 Старая Бельгия\n+7 (384) 276-55-03\n\n"
            "📞 Брассери Бельгия\n+7 (384) 233 20 07"
        )

    elif text == "📍 Адрес":
        await update.message.reply_text(
            "📍 Старая Бельгия:\nКемерово, Красноармейская улица, 129\n\n"
            "📍 Брассери Бельгия:\nКемерово, Красноармейская улица, 144А"
        )

    elif text == "ℹ️ О нас":
        await update.message.reply_text(
            "Мы предлагаем Вам окунуться в атмосферу Бельгии, почувствовать себя путешественником, "
            "даже не уезжая из Кемерово. Огромный выбор бельгийского пива, фриты, бельгийские вафли и шоколад. "
            "Всё это Вы найдёте в баре \"Бельгия\"."
        )

    elif text == "🌐 Наш сайт":
        await update.message.reply_text(
            "🌐 Наш сайт: https://bar42.ru"
        )

# Name
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name_and_number"] = update.message.text
    await update.message.reply_text("🎟️ Введите номер билета:")
    return TICKET

# Ticket
async def get_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ticket"] = update.message.text
    await update.message.reply_text("📷 Пришлите фото билета:")
    return PHOTO

# Photo
async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("❌ Пожалуйста, отправьте фото")
        return PHOTO

    photo = update.message.photo[-1].file_id
    name_and_number = context.user_data["name_and_number"]
    ticket = context.user_data["ticket"]

    await update.message.reply_text(
        "✅ Регистрация успешно завершена! Удачи! 🍀",
        reply_markup=ReplyKeyboardRemove()
    )

    await context.bot.send_message(
        ADMIN_ID,
        f"📥 Новая заявка:\n👤 {name_and_number}\n🎟️ {ticket}"
    )
    await context.bot.send_photo(ADMIN_ID, photo)

    return ConversationHandler.END

# /help
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✏️ Напишите, что вы хотите:")
    return HELP

# Ответ на текст после /help
async def help_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # Сообщение пользователю
    await update.message.reply_text(
        "✅ Спасибо, ваш запрос получен! Мы свяжемся с вами в ближайшее время."
    )

    # Уведомление для администратора
    await context.bot.send_message(
        ADMIN_ID,
        f"ℹ️ Пользователь {update.effective_user.full_name} ({update.effective_user.id}) отправил запрос: {user_text}"
    )

    return ConversationHandler.END

# /challenge
async def challenge_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✍️ Введите ваше имя и номер:")
    return NAME

# Commands
async def set_commands(app):
    commands = [
        BotCommand("start", "Главное меню"),
        BotCommand("challenge", "Участвовать в розыгрыше"),
        BotCommand("help", "Запрос помощи"),
    ]
    await app.bot.set_my_commands(commands)

# Запуск бота
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("challenge", challenge_cmd),
            CommandHandler("help", help_cmd),
            MessageHandler(filters.TEXT & ~filters.COMMAND, menu),
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            TICKET: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_ticket)],
            PHOTO: [MessageHandler(filters.PHOTO, get_photo)],
            HELP: [MessageHandler(filters.TEXT & ~filters.COMMAND, help_response)],
        },
        fallbacks=[],
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("help", help_cmd))

    app.post_init = set_commands
    app.run_polling()
