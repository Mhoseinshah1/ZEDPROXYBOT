from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.entities import Receipt, Payment, User

router = Router()

@router.message(F.photo | F.document)
async def receipt_upload(message: Message):
    db = SessionLocal()
    try:
        u = db.scalar(select(User).where(User.telegram_id == message.from_user.id))
        pid = None
        if message.caption and message.caption.startswith('receipt '):
            pid = int(message.caption.split()[1])
        else:
            rows = db.scalars(select(Payment).where(Payment.user_id == u.id, Payment.status == 'pending').order_by(Payment.id.desc())).all()
            if len(rows) == 1: pid = rows[0].id
            elif len(rows) > 1:
                return await message.answer('چند پرداخت معلق دارید. لطفاً رسید را با کپشن receipt <payment_id> ارسال کنید.')
        if not pid:
            return await message.answer('پرداخت معلقی پیدا نشد.')
        file_id = message.photo[-1].file_id if message.photo else message.document.file_id
        db.add(Receipt(payment_id=pid, telegram_file_id=file_id, status='pending'))
        db.commit()
        await message.answer(f'رسید برای پرداخت #{pid} ثبت شد و در انتظار تایید ادمین است.')
    finally: db.close()
