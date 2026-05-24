from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.entities import User, VpnService
from app.services.vpn.adapters.sanaei_3xui import Sanaei3xUiAdapter

router = Router()

@router.message(F.text == "📦 سرویس‌های من")
async def services(message: Message):
    db = SessionLocal()
    try:
        u = db.scalar(select(User).where(User.telegram_id == message.from_user.id))
        sv = db.scalars(select(VpnService).where(VpnService.user_id == u.id)).all()
        await message.answer("\n".join([f"{s.id}) {s.client_email}" for s in sv]) or "سرویسی ندارید")
    finally: db.close()

@router.message(F.text.startswith("کانفیگ "))
async def config(message: Message):
    await message.answer("لطفاً از پنل ادمین ارسال شود.")
