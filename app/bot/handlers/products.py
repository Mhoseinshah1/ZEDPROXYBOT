from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.entities import Product

router = Router()

@router.message(F.text == "🛒 خرید VPN")
async def products(message: Message):
    db = SessionLocal()
    try:
        ps = db.scalars(select(Product).where(Product.is_active == True)).all()
        await message.answer("\n".join([f"{p.id}) {p.title} - {p.price}" for p in ps]) + "\nدستور: خرید <id>")
    finally: db.close()
