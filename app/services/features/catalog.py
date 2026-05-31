"""Feature catalog inspired by MirzaBot's public feature set.

The catalog is intentionally local and declarative so menus, seed data and
future admin settings can stay consistent without duplicating labels.
"""

USER_MENU_FEATURES = [
    ("buy", "🔐 خرید اشتراک"),
    ("wallet", "🏦 کیف پول + شارژ"),
    ("free", "اشتراک رایگان {تست}"),
    ("renew", "♻️ تمدید سرویس"),
    ("services", "🛍 سرویس‌های من"),
    ("tutorials", "📚 آموزش"),
    ("support", "🎫 پشتیبانی"),
    ("referral", "👥 زیر مجموعه گیری"),
    ("wheel", "🎲 گردونه شانس"),
    ("reseller", "درخواست نمایندگی"),
]

MIRZABOT_FEATURE_FLAGS = [
    *USER_MENU_FEATURES,
    ("phone_verification", "احراز شماره موبایل"),
    ("force_join", "عضویت اجباری کانال"),
    ("card_to_card", "پرداخت کارت‌به‌کارت"),
    ("nowpayments", "درگاه NowPayments"),
    ("aqayepardakht", "درگاه آقای پرداخت"),
    ("reports", "گزارش‌های خرید و تست"),
    ("faq", "سوالات متداول"),
    ("text_customization", "مدیریت متن‌های ربات"),
    ("panel_management", "مدیریت پنل و محصول"),
    ("protocol_settings", "تنظیمات پروتکل‌ها"),
    ("additional_volume", "خرید حجم اضافه"),
    ("service_link_update", "بروزرسانی لینک سرویس"),
]
