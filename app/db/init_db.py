from passlib.context import CryptContext
from sqlalchemy import select
from app.core.config import settings
from app.db.session import Base, engine, SessionLocal
from app.models.entities import Admin, BotText, AppDownload, Setting, Product, Tutorial, FeatureSetting

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if settings.main_admin_id and not db.scalar(select(Admin).where(Admin.telegram_id == settings.main_admin_id)):
            db.add(Admin(telegram_id=settings.main_admin_id, username=settings.admin_username, password_hash=pwd.hash(settings.admin_password or "change-me"), role="owner"))
        for k, v in {"welcome": "به ربات فروش VPN خوش آمدید 🌟", "payment_waiting": "رسید واریز را ارسال کنید.", "buy_success": "سرویس شما فعال شد ✅"}.items():
            if not db.scalar(select(BotText).where(BotText.key == k)): db.add(BotText(key=k, value=v))
        for p in ["android", "ios", "windows", "macos"]:
            if not db.scalar(select(AppDownload).where(AppDownload.platform == p)): db.add(AppDownload(platform=p, url="https://example.com"))
        defaults = {
            "report_chat_id": settings.report_group_chat_id or "", "card_number": settings.card_number,
            "card_holder": settings.card_holder, "bot_enabled": "true"
        }
        for k, v in defaults.items():
            if not db.scalar(select(Setting).where(Setting.key == k)): db.add(Setting(key=k, value=v or ""))
        feature_defaults = [
            ("buy", "خرید اشتراک"), ("wallet", "کیف پول + شارژ"), ("free", "اشتراک رایگان {تست}"),
            ("renew", "تمدید سرویس"), ("services", "سرویس‌های من"), ("tutorials", "آموزش"),
            ("referral", "زیر مجموعه گیری"), ("wheel", "گردونه شانس"), ("reseller", "درخواست نمایندگی"), ("support", "پشتیبانی")
        ]
        for i, (k, t) in enumerate(feature_defaults):
            if not db.scalar(select(FeatureSetting).where(FeatureSetting.key == k)):
                db.add(FeatureSetting(key=k, title=t, enabled=True, sort_order=i))
        if not db.scalar(select(Product).limit(1)): db.add(Product(title="اشتراک یک‌ماهه", category="ماهانه", price=250000, days=30, traffic_gb=100, is_active=True))
        if not db.scalar(select(Tutorial).limit(1)): db.add(Tutorial(title="راهنمای اتصال", category="عمومی", content="ابتدا اپ را نصب و سپس کانفیگ را وارد کنید."))
        db.commit()
    finally:
        db.close()
