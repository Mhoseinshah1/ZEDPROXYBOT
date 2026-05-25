from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from app.bot.keyboards.user import main_menu
from app.bot.utils import ensure_user, ensure_main_admin, is_admin

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    ensure_main_admin(message.from_user)
    ensure_user(message.from_user)
    await message.answer('به ربات فروش VPN خوش آمدید.', reply_markup=main_menu(is_admin(message.from_user.id)))
