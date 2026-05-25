from aiogram import Bot
from sqlalchemy.orm import Session
from app.models.entities import ReportLog


class ReportService:
    def __init__(self, bot: Bot | None, db: Session, chat_id: str | None, enabled: bool):
        self.bot = bot
        self.db = db
        self.chat_id = chat_id
        self.enabled = enabled

    async def emit(self, event_type: str, text: str, payload: dict, level: str = "info"):
        self.db.add(ReportLog(event_type=event_type, level=level, payload=payload))
        self.db.commit()
        if self.enabled and self.chat_id and self.bot:
            try:
                await self.bot.send_message(chat_id=int(self.chat_id), text=text)
            except Exception:
                pass
