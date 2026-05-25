from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.entities import Admin, Payment, Order, Wallet, Setting
from app.services.reports.service import ReportService
from app.services.vpn.provisioning import provision_paid_order

router = Router()

@router.message(F.text == "🛠 پنل ادمین")
async def admin_menu(message: Message):
    db = SessionLocal()
    try:
        if not db.scalar(select(Admin).where(Admin.telegram_id == message.from_user.id)):
            return await message.answer('دسترسی ندارید')
        pays = db.scalars(select(Payment).where(Payment.status == 'pending').limit(20)).all()
        if not pays: return await message.answer('پرداخت pending نداریم')
        for p in pays:
            kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='✅ تایید', callback_data=f'pay_ok:{p.id}'), InlineKeyboardButton(text='❌ رد', callback_data=f'pay_no:{p.id}')]])
            await message.answer(f"Payment #{p.id} مبلغ: {p.amount}", reply_markup=kb)
    finally: db.close()

@router.callback_query(F.data.startswith('pay_'))
async def pay_decision(call: CallbackQuery, bot: Bot):
    db = SessionLocal()
    try:
        admin = db.scalar(select(Admin).where(Admin.telegram_id == call.from_user.id))
        if not admin: return
        action, pid = call.data.split(':'); p = db.get(Payment, int(pid))
        report = ReportService(bot, db, db.scalar(select(Setting.value).where(Setting.key == 'report_chat_id')), True)
        if action == 'pay_ok':
            p.status = 'approved'
            if p.order_id:
                db.get(Order, p.order_id).status = 'paid'
                await provision_paid_order(p.order_id, db, bot=bot, report_service=report)
            else:
                w = db.scalar(select(Wallet).where(Wallet.user_id == p.user_id)); w.balance = float(w.balance) + float(p.amount); db.commit()
            await report.emit('payment_approved', f'✅ پرداخت تایید شد #{p.id}', {'payment_id': p.id})
        else:
            p.status = 'rejected'; db.commit()
            await report.emit('payment_rejected', f'❌ پرداخت رد شد #{p.id}', {'payment_id': p.id})
        await report.emit('admin_action', 'اقدام ادمین روی پرداخت', {'admin_id': admin.id, 'payment_id': p.id, 'action': action})
        await call.message.answer('انجام شد')
    except Exception as e:
        await call.message.answer(f'خطا: {e}')
    finally: db.close()
