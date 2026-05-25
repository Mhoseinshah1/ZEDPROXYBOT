from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, func
from app.bot.keyboards.admin import admin_main_kb
from app.bot.utils import is_admin
from app.db.session import SessionLocal
from app.models.entities import User, Order, Payment, VpnService, Ticket

router = Router()

@router.message(F.text == '🛠 پنل ادمین')
async def admin_menu(message: Message):
    if not is_admin(message.from_user.id):
        return await message.answer('دسترسی ندارید.')
    await message.answer('پنل مدیریت:', reply_markup=admin_main_kb())

@router.callback_query(F.data == 'adm:stats')
async def stats(call: CallbackQuery):
    db = SessionLocal()
    try:
        txt = f"کل کاربران: {db.scalar(select(func.count(User.id)))}\nپرداخت pending: {db.scalar(select(func.count(Payment.id)).where(Payment.status=='pending'))}\nسفارش‌ها: {db.scalar(select(func.count(Order.id)))}\nسرویس فعال: {db.scalar(select(func.count(VpnService.id)).where(VpnService.status=='active'))}\nتیکت باز: {db.scalar(select(func.count(Ticket.id)).where(Ticket.status=='open'))}"
        await call.message.answer(txt)
    finally: db.close()
