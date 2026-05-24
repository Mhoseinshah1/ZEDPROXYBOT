from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.entities import Admin, Payment, Order, Wallet, User

router = Router()

@router.message(F.text == "🛠 پنل ادمین")
async def admin_menu(message: Message):
    db = SessionLocal()
    try:
        if not db.scalar(select(Admin).where(Admin.telegram_id == message.from_user.id)):
            return await message.answer('دسترسی ندارید')
        pays = db.scalars(select(Payment).where(Payment.status == 'pending').limit(5)).all()
        if not pays: return await message.answer('پرداخت pending نداریم')
        for p in pays:
            kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='✅ تایید', callback_data=f'pay_ok:{p.id}'), InlineKeyboardButton(text='❌ رد', callback_data=f'pay_no:{p.id}')]])
            await message.answer(f"Payment #{p.id} مبلغ: {p.amount}", reply_markup=kb)
    finally: db.close()

@router.callback_query(F.data.startswith('pay_'))
async def pay_decision(call: CallbackQuery):
    db = SessionLocal()
    try:
        if not db.scalar(select(Admin).where(Admin.telegram_id == call.from_user.id)): return
        action, pid = call.data.split(':'); p = db.get(Payment, int(pid))
        if action == 'pay_ok':
            p.status = 'approved'
            if p.order_id: db.get(Order, p.order_id).status = 'paid'
            else:
                w = db.scalar(select(Wallet).where(Wallet.user_id == p.user_id)); w.balance = float(w.balance) + float(p.amount)
        else: p.status = 'rejected'
        db.commit(); await call.message.answer('انجام شد')
    finally: db.close()
