import logging
import os.path
import pathlib
import random

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

CITY, STREET, HNUMBER, CHOOSE = range(4)

NAME, CONTACT, MESSAGE, PHOTO = range(4)

current_house = []
report_unit = []


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Добро пожаловать. Бот по мониторингу капитального"
             "ремонта. Напишите /help чтобы узнать о его возможностях."
    )


async def helper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Возможные команды:"
             "/status - Получить текущий статус состояния ремонта"
             "/contacts - Получить список контактов"
             "/report - Подать жалобу на проблему"
    )


async def status(update: Update) -> int:
    reply_keyboard = [["Воронеж", "Бобров", "Семилуки", "Нововоронеж", "Лиски"]]
    await update.message.reply_text(
        "Выберите ваш город из списка.",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True,
        )
    )

    return CITY


async def choose(update: Update) -> int:
    if update.message.text == "Состояние ремонта":
        bot_path = "%s\\photos\\%s\\%s\\%s\\" % (os.getcwd(), current_house[0], current_house[1], current_house[2])
        photos_exists = pathlib.Path.exists(pathlib.Path(bot_path))
        if photos_exists:
            for x in os.listdir(bot_path):
                await update.message.reply_photo(
                    photo=open("%s\\%s" % (bot_path, x), "rb")
                )
        else:
            await update.message.reply_text(
                "Информация не найдена!"
            )
        return ConversationHandler.END
    elif update.message.text == "Состояние счета":
        if current_house[0] == "Воронеж" and current_house[1] == "Фридриха Энгельса" and current_house[2] == "21":
            await update.message.reply_text(
                "На счету дома находится: 570045.76 рублей",
            )
        else:
            await update.message.reply_text(
                "На счету дома находится: %s рублей." % random.randint(521740, 1585321),
            )

        return ConversationHandler.END

    await update.message.reply_text(
        "Что-то пошло не так. Повторите запрос.",
    )

    return ConversationHandler.END


async def city(update: Update) -> int:
    user = update.message.from_user
    logger.info("Выбранный город пользователя %s: %s", user.first_name, update.message.text)
    current_house.append(update.message.text)
    await update.message.reply_text(
        "Город выбран. Теперь введите улицу.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return STREET


async def street(update: Update) -> int:
    user = update.message.from_user
    logger.info("Улица пользователя %s: %s", user.first_name, update.message.text)
    current_house.append(update.message.text)
    await update.message.reply_text(
        "Улица выбрана. Теперь введите номер дома.",
    )

    return HNUMBER


async def hnumber(update: Update) -> int:
    reply_keyboard = [["Состояние ремонта", "Состояние счета"]]
    user = update.message.from_user
    logger.info("Номер дома пользователя %s: %s", user.first_name, update.message.text)
    current_house.append(update.message.text)
    await update.message.reply_text(
        "Номер выбран. "
        "Что вы хотите узнать?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        )
    )

    return CHOOSE


async def cancel(update: Update) -> int:
    await update.message.reply_text(
        "Вы вышли в главное меню!", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Адрес: 394036, г. Воронеж, ул. Фридриха Энгельса, д. 18"
             "Электронная почта: fond@fkr36.ru"
             "Тел.: +7 (473) 280-12-45"
    )


async def report(update: Update) -> int:
    await update.message.reply_text(
        "Введите ФИО",
    )

    return NAME


async def name(update: Update) -> int:
    report_unit.append(update.message.text)
    await update.message.reply_text(
        "Введите номер телефона",
    )

    return CONTACT


async def contact(update: Update) -> int:
    report_unit.append(update.message.text)
    await update.message.reply_text(
        "Опишите проблему",
    )

    return MESSAGE


async def message(update: Update) -> int:
    report_unit.append(update.message.text)
    await update.message.reply_text(
        "Приложите фотографии",
    )

    return PHOTO


async def photo(update: Update) -> int:
    await update.message.reply_text(
        "Спасибо за обращение. Оно будет рассмотрено и с вами свяжутся.",
    )

    return ConversationHandler.END


def main() -> None:
    application = ApplicationBuilder().token('5384971396:AAGarBwmPvoYZE9StojuAcHKz4oMfw2bRms').build()

    application.add_handler(CommandHandler(command="start", callback=start))
    application.add_handler(CommandHandler(command="help", callback=helper))

    status_conv_handler = ConversationHandler(
        entry_points=[CommandHandler(command="status", callback=status)],
        states={
            CITY: [MessageHandler(filters.Regex("^(Воронеж|Бобров|Семилуки|Нововоронеж|Лиски)$"), city)],
            STREET: [MessageHandler(filters.TEXT & ~filters.COMMAND, street)],
            HNUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, hnumber)],
            CHOOSE: [MessageHandler(filters.Regex("^(Состояние счета|Состояние ремонта)$"), choose)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(status_conv_handler)

    report_conv_handler = ConversationHandler(
        entry_points=[CommandHandler(command="report", callback=report)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, contact)],
            MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, message)],
            PHOTO: [MessageHandler(filters.PHOTO, photo)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(report_conv_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
