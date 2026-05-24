from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.entities import User, Product, Order, Payment

router = Router()

@router.message(F.text.startswith("خرید "))
async def buy(message: Message):
    db = SessionLocal()
    try:
        pid = int(message.text.split()[1])
        u = db.scalar(select(User).where(User.telegram_id == message.from_user.id)); p = db.get(Product, pid)
        if not p: return await message.answer("محصول نامعتبر")
        o = Order(order_code=f"ORD-{u.id}-{pid}-{u.telegram_id}", user_id=u.id, product_id=p.id, amount=p.price)
        db.add(o); db.commit(); db.refresh(o)
        pay = Payment(order_id=o.id, user_id=u.id, amount=p.price, method='card_to_card', status='pending')
        db.add(pay); db.commit(); db.refresh(pay)
        await message.answer(f"سفارش {o.order_code} ثبت شد. رسید را ارسال کنید با کپشن receipt {pay.id}")
    finally: db.close()
