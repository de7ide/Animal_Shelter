import asyncio
from redis.asyncio import Redis

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage

from config_data.config import Config, load_config
from middlewares.db import DataBaseSession
from database.engine import create_db, drop_db, session_maker
from handlers.user_private import user_private_router
from handlers.admin_private import admin_router
from common.bot_cmds_list import private


config: Config = load_config()

redis = Redis(host='localhost')
storage = RedisStorage(redis=redis)

bot = Bot(
    token=config.token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher(storage=storage)

dp.include_router(user_private_router)
dp.include_router(admin_router)


async def on_startup(bot):
    await create_db()


async def main():
    dp.startup.register(on_startup)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(private)
    await dp.start_polling(bot)

asyncio.run(main())
