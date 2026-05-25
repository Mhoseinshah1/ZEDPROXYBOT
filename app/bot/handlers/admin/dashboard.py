from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, func
from app.bot.utils import is_admin
from app.db.session import SessionLocal
from app.models.entities import User, Order, Payment, VpnService, Ticket, VpnPanel, ReportLog, FeatureSetting, Setting

router = Router()

@router.message(F.text == '🛠 پنل ادمین')
async def admin_menu(message: Message):
    if not is_admin(message.from_user.id): return await message.answer('دسترسی ندارید.')
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📊 آمار', callback_data='adm:stats'), InlineKeyboardButton(text='🧾 رسیدهای تأییدنشده', callback_data='adm:payments')],
        [InlineKeyboardButton(text='🖥 پنل‌های 3x-ui', callback_data='adm:panels'), InlineKeyboardButton(text='⚙️ تنظیمات', callback_data='adm:settings')],
    ])
    await message.answer('پنل مدیریت', reply_markup=kb)

@router.callback_query(F.data == 'adm:stats')
async def stats(call: CallbackQuery):
    db = SessionLocal()
    try:
        txt=f"کل کاربران: {db.scalar(select(func.count(User.id)))}\nسفارش‌ها: {db.scalar(select(func.count(Order.id)))}\nپرداخت معلق: {db.scalar(select(func.count(Payment.id)).where(Payment.status=='pending'))}\nسرویس فعال: {db.scalar(select(func.count(VpnService.id)).where(VpnService.status=='active'))}\nتیکت باز: {db.scalar(select(func.count(Ticket.id)).where(Ticket.status=='open'))}\nخطاهای اخیر: {db.scalar(select(func.count(ReportLog.id)).where(ReportLog.level=='error'))}"
        await call.message.answer(txt)
    finally: db.close()

@router.callback_query(F.data == 'adm:settings')
async def settings_menu(call: CallbackQuery):
    db=SessionLocal()
    try:
        bot_enabled = db.scalar(select(Setting.value).where(Setting.key=='bot_enabled')) or 'true'
        kb=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='روشن/خاموش کل بات', callback_data='admset:bot')],[InlineKeyboardButton(text='مدیریت دکمه خرید', callback_data='admset:buy')]])
        await call.message.answer(f"وضعیت bot_enabled: {bot_enabled}", reply_markup=kb)
    finally: db.close()

@router.callback_query(F.data.startswith('admset:'))
async def settings_toggle(call: CallbackQuery):
    db=SessionLocal()
    try:
        key = call.data.split(':')[1]
        if key == 'bot':
            s = db.scalar(select(Setting).where(Setting.key=='bot_enabled'))
            if not s: s = Setting(key='bot_enabled', value='true'); db.add(s)
            s.value = 'false' if s.value == 'true' else 'true'; db.commit(); await call.message.answer(f"وضعیت بات: {s.value}")
        elif key == 'buy':
            fs = db.scalar(select(FeatureSetting).where(FeatureSetting.key=='buy'))
            if not fs: fs = FeatureSetting(key='buy', title='خرید اشتراک', enabled=True); db.add(fs)
            fs.enabled = not fs.enabled; db.commit(); await call.message.answer(f"خرید اشتراک: {'روشن' if fs.enabled else 'خاموش'}")
    finally: db.close()

@router.callback_query(F.data == 'adm:panels')
async def panels(call: CallbackQuery):
    db = SessionLocal()
    try:
        rows = db.scalars(select(VpnPanel)).all()
        txt = '\n'.join([f"{p.id}) {p.name} {p.host}:{p.port}" for p in rows]) or 'پنلی ثبت نشده.'
        await call.message.answer(txt + '\nبرای افزودن از API استفاده کنید. تست/سینک در دکمه رسیدها در نسخه بعدی تکمیل می‌شود.')
    finally: db.close()
