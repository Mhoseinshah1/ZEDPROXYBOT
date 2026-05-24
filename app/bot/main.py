import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from app.core.config import settings

bot = Bot(settings.bot_token)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(msg: Message):
    await msg.answer('سلام 👋 به ربات فروش VPN خوش آمدید.')


async def run_polling():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(run_polling())
