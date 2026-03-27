#!/usr/bin/env python
"""
Точка входа для запуска Telegram бота в режиме long polling
"""

import asyncio
import os
import sys

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.bot.dispatcher import create_bot, create_dispatcher


async def main():
    """Запуск бота в режиме polling"""
    bot = create_bot()
    dp = create_dispatcher()
    
    print("Starting Telegram bot polling...")
    print("Bot is ready to receive messages")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())