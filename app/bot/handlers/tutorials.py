from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.entities import Tutorial

router = Router()

@router.message(F.text == "🎓 آموزش‌ها")
async def tutorials(message: Message):
    db = SessionLocal()
    try:
        rows = db.scalars(select(Tutorial)).all()
        await message.answer("\n\n".join([f"{r.title}\n{r.content}" for r in rows]) or "خالی")
    finally: db.close()
