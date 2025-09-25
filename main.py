
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from .config import BOT_TOKEN
from .handlers import start as start_handlers
from .handlers import tutor as tutor_handlers
from .handlers import misc as misc_handlers

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(start_handlers.router)
    dp.include_router(tutor_handlers.router)
    dp.include_router(misc_handlers.router)
    logging.info("Math Coach bot is running (long polling)...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
