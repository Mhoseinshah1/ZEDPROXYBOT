from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.entities import User, Wallet

router = Router()

@router.message(F.text == "👤 پروفایل")
async def profile(message: Message):
    db = SessionLocal()
    try:
        u = db.scalar(select(User).where(User.telegram_id == message.from_user.id))
        w = db.scalar(select(Wallet).where(Wallet.user_id == u.id)) if u else None
        await message.answer(f"نام: {u.full_name if u else '-'}\nموجودی: {w.balance if w else 0}")
    finally: db.close()
