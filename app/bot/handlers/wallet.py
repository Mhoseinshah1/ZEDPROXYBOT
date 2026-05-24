from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.entities import User, Wallet, Payment

router = Router()

@router.message(F.text == "💼 کیف پول")
async def wallet(message: Message):
    db = SessionLocal()
    try:
        u = db.scalar(select(User).where(User.telegram_id == message.from_user.id)); w = db.scalar(select(Wallet).where(Wallet.user_id == u.id))
        await message.answer(f"موجودی: {w.balance}\nبرای شارژ: شارژ 50000")
    finally: db.close()

@router.message(F.text.startswith("شارژ "))
async def topup(message: Message):
    db = SessionLocal()
    try:
        amount = float(message.text.split()[1]); u = db.scalar(select(User).where(User.telegram_id == message.from_user.id))
        p = Payment(user_id=u.id, amount=amount, method='card_to_card', status='pending')
        db.add(p); db.commit(); db.refresh(p)
        await message.answer(f"پرداخت #{p.id}\nمبلغ: {amount}\nکارت: {settings.card_number}\nرسید را عکس/فایل بفرستید و کپشن: receipt {p.id}")
    finally: db.close()
