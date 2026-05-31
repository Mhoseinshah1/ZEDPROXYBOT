from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.entities import User, Ticket, TicketMessage, Setting
from app.services.reports.service import ReportService

router = Router()

@router.message((F.text == "🎫 ثبت تیکت") | (F.text == "🎫 پشتیبانی"))
async def new_ticket(message: Message):
    db = SessionLocal()
    try:
        u = db.scalar(select(User).where(User.telegram_id == message.from_user.id))
        t = Ticket(user_id=u.id, title='تیکت', category='general', status='open')
        db.add(t); db.commit(); db.refresh(t)
        db.add(TicketMessage(ticket_id=t.id, sender_type='user', body='درخواست پشتیبانی')); db.commit()
        chat_id = db.query(Setting.value).filter(Setting.key=='report_chat_id').scalar()
        await ReportService(message.bot, db, chat_id, True).emit('ticket_created', f'🎫 تیکت جدید #{t.id}', {'ticket_id': t.id})
        await message.answer(f"تیکت #{t.id} ثبت شد")
    finally: db.close()
