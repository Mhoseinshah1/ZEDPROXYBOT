from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def admin_main_kb():
    rows = [
        [InlineKeyboardButton(text='📊 آمار', callback_data='adm:stats'), InlineKeyboardButton(text='👥 کاربران', callback_data='adm:users')],
        [InlineKeyboardButton(text='🧾 پرداخت‌های در انتظار', callback_data='adm:payments'), InlineKeyboardButton(text='🛒 سفارش‌ها', callback_data='adm:orders')],
        [InlineKeyboardButton(text='📦 سرویس‌ها', callback_data='adm:services'), InlineKeyboardButton(text='🎫 تیکت‌ها', callback_data='adm:tickets')],
        [InlineKeyboardButton(text='🖥 پنل‌های 3x-ui', callback_data='adm:panels'), InlineKeyboardButton(text='📜 گزارش‌ها', callback_data='adm:reports')],
        [InlineKeyboardButton(text='⚙️ تنظیمات', callback_data='adm:settings')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)
