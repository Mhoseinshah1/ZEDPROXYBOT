from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, func
from app.db.session import SessionLocal
from app.models.entities import User, Wallet, Order, VpnService

router = Router()

@router.message(F.text == '👤 پروفایل')
async def profile(message: Message):
    db = SessionLocal()
    try:
        u = db.scalar(select(User).where(User.telegram_id == message.from_user.id))
        w = db.scalar(select(Wallet).where(Wallet.user_id == u.id))
        orders = db.scalar(select(func.count(Order.id)).where(Order.user_id == u.id))
        active = db.scalar(select(func.count(VpnService.id)).where(VpnService.user_id == u.id, VpnService.status == 'active'))
        txt = f"نام: {u.full_name or '-'}\nآیدی: {u.telegram_id}\nیوزرنیم: @{u.username or '-'}\nموبایل: {u.phone or '-'}\nموجودی: {w.balance}\nتعداد سفارش: {orders}\nسرویس فعال: {active}\nوضعیت: {'مسدود' if u.is_blocked else 'فعال'}"
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='💼 کیف پول', callback_data='go:wallet'), InlineKeyboardButton(text='📦 سرویس‌های من', callback_data='go:services')],[InlineKeyboardButton(text='🧾 سفارش‌های من', callback_data='go:orders')]])
        await message.answer(txt, reply_markup=kb)
    finally: db.close()
