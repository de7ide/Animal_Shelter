import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

from middlewares.db import DataBaseSession
from database.engine import create_db, drop_db, session_maker
from handlers.user_private import user_private_router
from handlers.admin_private import admin_router
from common.bot_cmds_list import private


bot = Bot(token=os.getenv('BOT_TOKEN'), parse_mode=ParseMode.HTML)

dp = Dispatcher()

dp.include_router(user_private_router)
dp.include_router(admin_router)


async def on_startup(bot):
    await create_db()


async def on_shutdown(bot):
    print('бот лег')


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(private)
    await dp.start_polling(bot)

asyncio.run(main())
