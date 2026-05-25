from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, func
from app.bot.utils import is_admin
from app.bot.states import AdminStates
from app.db.session import SessionLocal
from app.models.entities import User, Order, Payment, VpnService, Ticket, VpnPanel, ReportLog, FeatureSetting, Setting, AuditLog

router = Router()

def _set(db, key, value):
    s = db.scalar(select(Setting).where(Setting.key == key))
    if not s:
        s = Setting(key=key, value=str(value)); db.add(s)
    else:
        s.value = str(value)

@router.message(F.text == '🛠 پنل ادمین')
async def admin_menu(message: Message):
    if not is_admin(message.from_user.id): return await message.answer('دسترسی ندارید.')
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📊 آمار', callback_data='adm:stats'), InlineKeyboardButton(text='🧾 رسیدهای تأییدنشده', callback_data='adm:payments')],
        [InlineKeyboardButton(text='🖥 پنل‌های 3x-ui', callback_data='adm:panels'), InlineKeyboardButton(text='⚙️ تنظیمات', callback_data='adm:settings')],
    ])
    await message.answer('پنل مدیریت', reply_markup=kb)

@router.callback_query(F.data == 'adm:settings')
async def settings_menu(call: CallbackQuery):
    kb=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='💳 تنظیمات مالی', callback_data='admset:financial')],
        [InlineKeyboardButton(text='روشن/خاموش کل بات', callback_data='admset:bot')],
        [InlineKeyboardButton(text='مدیریت دکمه خرید', callback_data='admset:buy')]
    ])
    await call.message.answer('تنظیمات ادمین:', reply_markup=kb)

@router.callback_query(F.data == 'admset:financial')
async def financial_menu(call: CallbackQuery):
    db=SessionLocal()
    try:
        get=lambda k,d='': db.scalar(select(Setting.value).where(Setting.key==k)) or d
        txt=(f"شماره کارت: {get('card_number','-')}\nنام دارنده: {get('card_holder','-')}\n"
             f"فعال بودن کارت‌به‌کارت: {get('k2k_enabled','false')}\n"
             f"حداقل شارژ: {get('min_wallet_topup','10000')}\nحداکثر شارژ: {get('max_wallet_topup','')}\n"
             f"متن پرداخت: {get('payment_instructions','')}" )
        kb=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='1) تنظیم شماره کارت', callback_data='fin:set_card')],
            [InlineKeyboardButton(text='2) تنظیم نام دارنده', callback_data='fin:set_holder')],
            [InlineKeyboardButton(text='3) روشن/خاموش کارت‌به‌کارت', callback_data='fin:toggle_k2k')],
            [InlineKeyboardButton(text='4) تنظیم متن راهنما', callback_data='fin:set_instr')],
            [InlineKeyboardButton(text='5) حداقل شارژ', callback_data='fin:set_min')],
            [InlineKeyboardButton(text='6) حداکثر شارژ', callback_data='fin:set_max')],
            [InlineKeyboardButton(text='7) مشاهده تنظیمات فعلی', callback_data='admset:financial')],
        ])
        await call.message.answer(txt, reply_markup=kb)
    finally: db.close()

@router.callback_query(F.data.startswith('fin:'))
async def financial_actions(call: CallbackQuery, state: FSMContext):
    action=call.data.split(':')[1]
    if action=='set_card':
        await state.set_state(AdminStates.waiting_card_number); return await call.message.answer('شماره کارت جدید را وارد کنید:')
    if action=='set_holder':
        await state.set_state(AdminStates.waiting_card_holder); return await call.message.answer('نام صاحب کارت را وارد کنید:')
    if action=='set_instr':
        await state.set_state(AdminStates.waiting_payment_instructions); return await call.message.answer('متن راهنمای پرداخت را وارد کنید:')
    if action=='set_min':
        await state.set_state(AdminStates.waiting_min_topup); return await call.message.answer('حداقل شارژ کیف پول (تومان):')
    if action=='set_max':
        await state.set_state(AdminStates.waiting_max_topup); return await call.message.answer('حداکثر شارژ کیف پول (تومان، خالی=بدون سقف):')
    if action=='toggle_k2k':
        db=SessionLocal()
        try:
            cur = (db.scalar(select(Setting.value).where(Setting.key=='k2k_enabled')) or 'false').lower()=='true'
            _set(db,'k2k_enabled','false' if cur else 'true')
            db.add(AuditLog(action='setting_changed', payload={'key':'k2k_enabled','value':not cur}))
            db.add(ReportLog(event_type='setting_changed', level='info', payload={'key':'k2k_enabled','value':not cur}))
            db.commit(); await call.message.answer(f"کارت‌به‌کارت {'فعال' if not cur else 'غیرفعال'} شد.")
        finally: db.close()

@router.message(AdminStates.waiting_card_number)
async def set_card_number(message: Message, state: FSMContext):
    db=SessionLocal()
    try:
        _set(db,'card_number',message.text.strip()); db.add(AuditLog(action='setting_changed', payload={'key':'card_number'})); db.add(ReportLog(event_type='setting_changed', level='info', payload={'key':'card_number'})); db.commit(); await message.answer('شماره کارت ذخیره شد.')
    finally: db.close(); await state.clear()

@router.message(AdminStates.waiting_card_holder)
async def set_card_holder(message: Message, state: FSMContext):
    db=SessionLocal()
    try:
        _set(db,'card_holder',message.text.strip()); db.add(AuditLog(action='setting_changed', payload={'key':'card_holder'})); db.add(ReportLog(event_type='setting_changed', level='info', payload={'key':'card_holder'})); db.commit(); await message.answer('نام صاحب کارت ذخیره شد.')
    finally: db.close(); await state.clear()

@router.message(AdminStates.waiting_payment_instructions)
async def set_instr(message: Message, state: FSMContext):
    db=SessionLocal()
    try:
        _set(db,'payment_instructions',message.text.strip()); db.add(AuditLog(action='setting_changed', payload={'key':'payment_instructions'})); db.add(ReportLog(event_type='setting_changed', level='info', payload={'key':'payment_instructions'})); db.commit(); await message.answer('متن راهنما ذخیره شد.')
    finally: db.close(); await state.clear()

@router.message(AdminStates.waiting_min_topup)
async def set_min(message: Message, state: FSMContext):
    db=SessionLocal()
    try:
        _set(db,'min_wallet_topup',message.text.strip()); db.commit(); await message.answer('حداقل شارژ ذخیره شد.')
    finally: db.close(); await state.clear()

@router.message(AdminStates.waiting_max_topup)
async def set_max(message: Message, state: FSMContext):
    db=SessionLocal()
    try:
        _set(db,'max_wallet_topup',message.text.strip()); db.commit(); await message.answer('حداکثر شارژ ذخیره شد.')
    finally: db.close(); await state.clear()

@router.callback_query(F.data == 'adm:stats')
async def stats(call: CallbackQuery):
    db = SessionLocal()
    try:
        txt=f"کل کاربران: {db.scalar(select(func.count(User.id)))}\nسفارش‌ها: {db.scalar(select(func.count(Order.id)))}\nپرداخت معلق: {db.scalar(select(func.count(Payment.id)).where(Payment.status=='pending'))}\nسرویس فعال: {db.scalar(select(func.count(VpnService.id)).where(VpnService.status=='active'))}\nتیکت باز: {db.scalar(select(func.count(Ticket.id)).where(Ticket.status=='open'))}\nخطاهای اخیر: {db.scalar(select(func.count(ReportLog.id)).where(ReportLog.level=='error'))}"
        await call.message.answer(txt)
    finally: db.close()

@router.callback_query(F.data.startswith('admset:'))
async def settings_toggle(call: CallbackQuery):
    if call.data in ('admset:financial',):
        return
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
        await call.message.answer(txt + '\nبرای افزودن از API استفاده کنید.')
    finally: db.close()
