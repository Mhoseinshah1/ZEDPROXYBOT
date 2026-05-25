from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def main_menu(is_admin: bool = False):
    rows = [
        [KeyboardButton(text='👤 پروفایل'), KeyboardButton(text='💼 کیف پول')],
        [KeyboardButton(text='🛒 خرید VPN'), KeyboardButton(text='🔄 تمدید VPN')],
        [KeyboardButton(text='📦 سرویس‌های من'), KeyboardButton(text='🎫 پشتیبانی')],
        [KeyboardButton(text='🎓 آموزش‌ها'), KeyboardButton(text='📲 دانلود اپ‌ها')],
    ]
    if is_admin:
        rows.append([KeyboardButton(text='🛠 پنل ادمین')])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🔙 بازگشت', callback_data='menu:back')]])
