from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.bot.handlers import router
from app.core.config import settings


def create_bot() -> Bot:
    """
    Создание и настройка экземпляра бота
    """
    return Bot(
        token=settings.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )


def create_dispatcher() -> Dispatcher:
    """
    Создание и настройка диспетчера с подключенными обработчиками
    """
    dp = Dispatcher()
    dp.include_router(router)
    return dp


async def start_bot():
    """
    Запуск бота (для отдельного запуска вне FastAPI)
    """
    bot = create_bot()
    dp = create_dispatcher()
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()