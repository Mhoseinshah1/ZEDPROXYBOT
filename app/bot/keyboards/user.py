from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.entities import FeatureSetting

DEFAULTS = [
    ('buy', '🔐 خرید اشتراک'), ('wallet', '🏦 کیف پول + شارژ'), ('free', 'اشتراک رایگان {تست}'),
    ('renew', '♻️ تمدید سرویس'), ('services', '🛍 سرویس‌های من'), ('tutorials', '📚 آموزش'),
    ('referral', '👥 زیر مجموعه گیری'), ('wheel', '🎲 گردونه شانس'), ('reseller', 'درخواست نمایندگی'),
]

def main_menu(is_admin: bool = False):
    db = SessionLocal()
    try:
        enabled = {x.key: x.enabled for x in db.scalars(select(FeatureSetting)).all()}
    finally:
        db.close()
    buttons = [label for key, label in DEFAULTS if enabled.get(key, True)]
    rows = [[KeyboardButton(text=b)] for b in buttons]
    if is_admin:
        rows.append([KeyboardButton(text='🛠 پنل ادمین')])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
