from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy import select
from app.bot.keyboards.user import main_menu
from app.bot.utils import ensure_user, ensure_main_admin, is_admin
from app.db.session import SessionLocal
from app.models.entities import Setting

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    ensure_main_admin(message.from_user)
    ensure_user(message.from_user)
    db = SessionLocal()
    try:
        bot_enabled = db.scalar(select(Setting.value).where(Setting.key == 'bot_enabled')) or 'true'
    finally:
        db.close()
    if bot_enabled.lower() != 'true' and not is_admin(message.from_user.id):
        return await message.answer('ربات موقتاً غیرفعال است.')
    await message.answer('به ربات فروش VPN خوش آمدید.', reply_markup=main_menu(is_admin(message.from_user.id)))
