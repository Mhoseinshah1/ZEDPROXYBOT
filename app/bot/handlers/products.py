from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.entities import Product

router = Router()

@router.message(F.text == '🛒 خرید VPN')
async def list_products(message: Message):
    db = SessionLocal()
    try:
        ps = db.scalars(select(Product).where(Product.is_active == True)).all()
        if not ps:
            return await message.answer('محصول فعالی موجود نیست.')
        rows = [[InlineKeyboardButton(text=f"{p.title} | {p.price} | {p.days} روز | {p.traffic_gb}GB", callback_data=f'prd:det:{p.id}') ] for p in ps]
        await message.answer('محصولات فعال:', reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    finally: db.close()

@router.callback_query(F.data.startswith('prd:det:'))
async def product_detail(call: CallbackQuery):
    pid = int(call.data.split(':')[-1])
    db = SessionLocal()
    try:
        p = db.get(Product, pid)
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🛒 خرید', callback_data=f'prd:buy:{p.id}')]])
        await call.message.answer(f"{p.title}\nقیمت: {p.price}\nمدت: {p.days} روز\nحجم: {p.traffic_gb}GB", reply_markup=kb)
    finally: db.close()
