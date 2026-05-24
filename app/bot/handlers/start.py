from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from .common import ensure_user
from app.db.session import SessionLocal
from app.services.reports.service import ReportService
from app.models.entities import Setting

router = Router()
kb_main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="👤 پروفایل"), KeyboardButton(text="💼 کیف پول")],
    [KeyboardButton(text="🛒 خرید VPN"), KeyboardButton(text="📦 سرویس‌های من")],
    [KeyboardButton(text="🎫 ثبت تیکت"), KeyboardButton(text="🎓 آموزش‌ها")],
    [KeyboardButton(text="🛠 پنل ادمین")],
], resize_keyboard=True)

@router.message(CommandStart())
async def start(message: Message):
    uid = ensure_user(message)
    db = SessionLocal()
    try:
        chat_id = db.query(Setting.value).filter(Setting.key=="report_chat_id").scalar()
        await ReportService(message.bot, db, chat_id, True).emit("user_created", "👤 کاربر جدید", {"user_id": uid})
    finally:
        db.close()
    await message.answer("به ربات خوش آمدید", reply_markup=kb_main)
