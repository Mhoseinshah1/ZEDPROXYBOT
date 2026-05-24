from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.entities import Receipt, Payment

router = Router()

@router.message(F.photo | F.document)
async def receipt_upload(message: Message):
    if not message.caption or not message.caption.startswith("receipt "):
        return
    pid = int(message.caption.split()[1])
    file_id = message.photo[-1].file_id if message.photo else message.document.file_id
    db = SessionLocal()
    try:
        p = db.get(Payment, pid)
        if not p: return await message.answer("پرداخت نامعتبر")
        db.add(Receipt(payment_id=pid, telegram_file_id=file_id, status='pending'))
        db.commit()
        await message.answer("رسید ثبت شد و در انتظار تایید ادمین است")
    finally: db.close()
