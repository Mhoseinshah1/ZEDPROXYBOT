from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from app.bot.states import WalletStates
from app.db.session import SessionLocal
from app.models.entities import User, Wallet, Payment, WalletTransaction, Setting, ReportLog

router = Router()

def get_setting(db, key, default=''):
    return db.scalar(select(Setting.value).where(Setting.key == key)) or default

@router.message(F.text == '🏦 کیف پول + شارژ')
async def wallet_menu(message: Message):
    db = SessionLocal()
    try:
        u = db.scalar(select(User).where(User.telegram_id == message.from_user.id)); w = db.scalar(select(Wallet).where(Wallet.user_id == u.id))
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='➕ شارژ کیف پول', callback_data='wallet:topup')],[InlineKeyboardButton(text='🧾 تاریخچه تراکنش‌ها', callback_data='wallet:history')]])
        await message.answer(f"موجودی فعلی: {w.balance} تومان", reply_markup=kb)
    finally: db.close()

@router.callback_query(F.data == 'wallet:topup')
async def topup_prompt(call: CallbackQuery, state: FSMContext):
    await state.set_state(WalletStates.waiting_amount)
    await call.message.answer('مبلغ شارژ را به تومان وارد کنید (مثال: 50000)')

@router.message(WalletStates.waiting_amount)
async def topup_create(message: Message, state: FSMContext):
    db = SessionLocal()
    try:
        amount = float(message.text.strip())
        k2k_enabled = get_setting(db, 'k2k_enabled', 'false').lower() == 'true'
        card_number = get_setting(db, 'card_number', '')
        card_holder = get_setting(db, 'card_holder', '')
        payment_instructions = get_setting(db, 'payment_instructions', 'پس از واریز رسید را ارسال کنید.')
        min_topup = float(get_setting(db, 'min_wallet_topup', '10000') or 10000)
        max_topup_raw = get_setting(db, 'max_wallet_topup', '')
        max_topup = float(max_topup_raw) if max_topup_raw else None
        if amount < min_topup:
            return await message.answer(f'حداقل مبلغ شارژ {int(min_topup)} تومان است.')
        if max_topup and amount > max_topup:
            return await message.answer(f'حداکثر مبلغ شارژ {int(max_topup)} تومان است.')
        if not k2k_enabled or not card_number or not card_holder:
            db.add(ReportLog(event_type='admin_action', level='warning', payload={'warn': 'k2k_not_configured'})); db.commit()
            return await message.answer('درگاه کارت‌به‌کارت هنوز توسط مدیریت تنظیم نشده است.')

        u = db.scalar(select(User).where(User.telegram_id == message.from_user.id))
        p = Payment(user_id=u.id, amount=amount, payment_type='wallet_topup', method='card_to_card', status='pending')
        db.add(p); db.commit(); db.refresh(p)
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='📋 کپی مبلغ', callback_data=f'copy:amt:{int(amount)}'), InlineKeyboardButton(text='💳 کپی کارت', callback_data=f'copy:card:{card_number}')]])
        await message.answer(f"پرداخت شارژ #{p.id}\nمبلغ: {amount}\nشماره کارت: {card_number}\nنام دارنده: {card_holder}\n{payment_instructions}\nرسید را به‌صورت عکس یا فایل با کپشن receipt {p.id} ارسال کنید.", reply_markup=kb)
    finally:
        db.close(); await state.clear()

@router.callback_query(F.data == 'wallet:history')
async def wallet_history(call: CallbackQuery):
    db = SessionLocal()
    try:
        u = db.scalar(select(User).where(User.telegram_id == call.from_user.id))
        rows = db.scalars(select(WalletTransaction).where(WalletTransaction.user_id == u.id).order_by(WalletTransaction.id.desc()).limit(10)).all()
        txt = '\n'.join([f"{r.id}: {r.amount} | {r.tx_type} | {r.status}" for r in rows]) or 'تراکنشی یافت نشد.'
        await call.message.answer(txt)
    finally: db.close()
