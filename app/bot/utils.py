from sqlalchemy import select
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.entities import Admin, User, Wallet


def ensure_main_admin(telegram_user):
    db = SessionLocal()
    try:
        tg_id = telegram_user.id
        if settings.main_admin_id and tg_id == settings.main_admin_id:
            admin = db.scalar(select(Admin).where(Admin.telegram_id == tg_id))
            if not admin:
                db.add(Admin(telegram_id=tg_id, username=settings.admin_username or 'owner', password_hash='-', role='owner', is_active=True))
            else:
                admin.role = 'owner'; admin.is_active = True
            db.commit()
    finally:
        db.close()


def is_owner(telegram_id: int) -> bool:
    if settings.main_admin_id and telegram_id == settings.main_admin_id:
        return True
    db = SessionLocal()
    try:
        a = db.scalar(select(Admin).where(Admin.telegram_id == telegram_id, Admin.role == 'owner', Admin.is_active == True))
        return bool(a)
    finally:
        db.close()


def is_admin(telegram_id: int) -> bool:
    if settings.main_admin_id and telegram_id == settings.main_admin_id:
        return True
    db = SessionLocal()
    try:
        a = db.scalar(select(Admin).where(Admin.telegram_id == telegram_id, Admin.is_active == True))
        return bool(a)
    finally:
        db.close()


def ensure_user(telegram_user):
    db = SessionLocal()
    try:
        u = db.scalar(select(User).where(User.telegram_id == telegram_user.id))
        if not u:
            u = User(telegram_id=telegram_user.id, username=telegram_user.username, full_name=telegram_user.full_name)
            db.add(u); db.commit(); db.refresh(u)
            db.add(Wallet(user_id=u.id, balance=0)); db.commit()
        return u.id
    finally:
        db.close()
