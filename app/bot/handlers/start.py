from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from .common import ensure_user

router = Router()
kb_main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="👤 پروفایل"), KeyboardButton(text="💼 کیف پول")],
    [KeyboardButton(text="🛒 خرید VPN"), KeyboardButton(text="📦 سرویس‌های من")],
    [KeyboardButton(text="🎫 ثبت تیکت"), KeyboardButton(text="🎓 آموزش‌ها")],
    [KeyboardButton(text="🛠 پنل ادمین")],
], resize_keyboard=True)

@router.message(CommandStart())
async def start(message: Message):
    ensure_user(message)
    await message.answer("به ربات خوش آمدید", reply_markup=kb_main)
