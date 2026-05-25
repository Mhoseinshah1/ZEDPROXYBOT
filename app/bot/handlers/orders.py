from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.entities import User, Product, Order, Payment, Wallet

router = Router()

@router.callback_query(F.data.startswith('prd:buy:'))
async def buy_product(call: CallbackQuery):
    pid = int(call.data.split(':')[-1])
    db = SessionLocal()
    try:
        u = db.scalar(select(User).where(User.telegram_id == call.from_user.id)); p = db.get(Product, pid)
        o = Order(order_code=f"ORD-{u.id}-{pid}-{u.telegram_id}", user_id=u.id, product_id=p.id, amount=p.price)
        db.add(o); db.commit(); db.refresh(o)
        pay = Payment(order_id=o.id, user_id=u.id, amount=p.price, method='card_to_card', status='pending')
        db.add(pay); db.commit(); db.refresh(pay)
        w = db.scalar(select(Wallet).where(Wallet.user_id == u.id))
        if float(w.balance) >= float(p.price):
            await call.message.answer(f"سفارش {o.order_code} ثبت شد. شما موجودی کافی دارید؛ برای کسر کیف پول به ادمین پیام دهید یا کارت‌به‌کارت انجام دهید.")
        await call.message.answer(f"پرداخت سفارش #{pay.id}\nمبلغ: {p.price}\nکارت: {settings.card_number}\nرسید را با کپشن receipt {pay.id} ارسال کنید.")
    finally: db.close()
