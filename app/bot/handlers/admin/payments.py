from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from app.bot.utils import is_admin
from app.db.session import SessionLocal
from app.models.entities import Payment, Order, Wallet, Receipt
from app.services.vpn.provisioning import provision_paid_order

router = Router()

@router.callback_query(F.data == 'adm:payments')
async def list_pending(call: CallbackQuery):
    if not is_admin(call.from_user.id): return
    db = SessionLocal()
    try:
        pays = db.scalars(select(Payment).where(Payment.status=='pending').order_by(Payment.id.desc()).limit(20)).all()
        if not pays: return await call.message.answer('پرداخت معلقی نیست.')
        for p in pays:
            rc = db.scalar(select(Receipt).where(Receipt.payment_id==p.id).order_by(Receipt.id.desc()))
            kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='✅ تایید', callback_data=f'admp:ok:{p.id}'), InlineKeyboardButton(text='❌ رد', callback_data=f'admp:no:{p.id}')]])
            await call.message.answer(f"Payment #{p.id} | مبلغ {p.amount} | نوع {'سفارش' if p.order_id else 'شارژ'} | رسید: {'دارد' if rc else 'ندارد'}", reply_markup=kb)
    finally: db.close()

@router.callback_query(F.data.startswith('admp:'))
async def decision(call: CallbackQuery, bot: Bot):
    if not is_admin(call.from_user.id): return
    _, action, pid = call.data.split(':')
    db = SessionLocal()
    try:
        p = db.get(Payment, int(pid))
        if action == 'ok':
            p.status = 'approved'; db.commit()
            if p.order_id:
                try:
                    await provision_paid_order(p.order_id, db, bot=bot)
                except Exception as e:
                    o = db.get(Order, p.order_id); o.status='provision_failed'; db.commit(); return await call.message.answer(f'پرداخت تایید شد ولی ساخت سرویس خطا داد: {e}')
            else:
                w = db.scalar(select(Wallet).where(Wallet.user_id==p.user_id)); w.balance=float(w.balance)+float(p.amount); db.commit()
            await call.message.answer('پرداخت تایید شد.')
        else:
            p.status='rejected'
            if p.order_id: db.get(Order,p.order_id).status='payment_rejected'
            db.commit(); await call.message.answer('پرداخت رد شد.')
    finally: db.close()
