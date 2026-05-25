from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, BufferedInputFile
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.entities import User, VpnService, ReportLog
from app.services.vpn.adapters.sanaei_3xui import Sanaei3xUiAdapter

router = Router()

@router.message(F.text == '🛍 سرویس‌های من')
async def services(message: Message):
    db = SessionLocal()
    try:
        u = db.scalar(select(User).where(User.telegram_id == message.from_user.id))
        sv = db.scalars(select(VpnService).where(VpnService.user_id == u.id)).all()
        if not sv: return await message.answer('سرویسی ندارید.')
        for s in sv:
            kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='ℹ️ مشخصات سرویس', callback_data=f'svc:info:{s.id}'),InlineKeyboardButton(text='🔗 دریافت لینک اشتراک', callback_data=f'svc:link:{s.id}')],[InlineKeyboardButton(text='▣ دریافت QR', callback_data=f'svc:qr:{s.id}')]])
            await message.answer(f"{s.client_email} | {s.status}", reply_markup=kb)
    finally: db.close()

@router.callback_query(F.data.startswith('svc:'))
async def service_actions(call: CallbackQuery):
    _, action, sid = call.data.split(':')
    db = SessionLocal()
    try:
        s = db.get(VpnService, int(sid))
        if action == 'info':
            await call.message.answer(f"email: {s.client_email}\nوضعیت: {s.status}\nشروع: {s.started_at}\nپایان: {s.expires_at}\nحجم کل: {s.total_gb}GB\nمصرف: {s.used_traffic_gb}GB\nیادداشت: {s.note or '-'}")
        elif action == 'link':
            link = s.subscription_link or s.config_link
            if not link:
                db.add(ReportLog(event_type='internal_error', level='error', payload={'service_id': s.id, 'reason': 'missing_link'})); db.commit()
                return await call.message.answer('لینک این سرویس موجود نیست. به ادمین گزارش شد.')
            await call.message.answer(link)
        elif action == 'qr':
            link = s.subscription_link or s.config_link
            if not link:
                return await call.message.answer('لینک این سرویس موجود نیست.')
            qr = Sanaei3xUiAdapter.qrcode_png_bytes(link)
            await call.message.answer_photo(BufferedInputFile(qr, filename='service_qr.png'))
    finally: db.close()
