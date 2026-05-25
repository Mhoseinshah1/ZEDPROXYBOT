from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.entities import User, Wallet


def ensure_user(message):
    db = SessionLocal()
    try:
        u = db.scalar(select(User).where(User.telegram_id == message.from_user.id))
        if not u:
            u = User(telegram_id=message.from_user.id, username=message.from_user.username, full_name=message.from_user.full_name)
            db.add(u); db.commit(); db.refresh(u)
            db.add(Wallet(user_id=u.id, balance=0)); db.commit()
        return u.id
    finally:
        db.close()
