import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy import select
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.entities import User, Wallet, Product, Ticket, TicketMessage, Order, Payment, Receipt, VpnService, Tutorial, AppDownload, Admin

kb_main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="👤 پروفایل"), KeyboardButton(text="💼 کیف پول")],
    [KeyboardButton(text="🛒 خرید VPN"), KeyboardButton(text="🔄 تمدید VPN")],
    [KeyboardButton(text="📦 سرویس‌های من"), KeyboardButton(text="🎓 آموزش‌ها")],
    [KeyboardButton(text="📲 اپ‌ها"), KeyboardButton(text="🎫 ثبت تیکت")],
    [KeyboardButton(text="🛠 پنل ادمین")],
], resize_keyboard=True)


def ensure_user(db, msg: Message):
    u = db.scalar(select(User).where(User.telegram_id == msg.from_user.id))
    if not u:
        u = User(telegram_id=msg.from_user.id, username=msg.from_user.username, full_name=msg.from_user.full_name)
        db.add(u); db.commit(); db.refresh(u)
        db.add(Wallet(user_id=u.id, balance=0)); db.commit()
    return u


async def start(m: Message):
    db = SessionLocal();
    try:
        ensure_user(db, m)
        await m.answer("به ربات فروش VPN خوش آمدید 🌟", reply_markup=kb_main)
    finally: db.close()


async def profile(m: Message):
    db = SessionLocal();
    try:
        u = ensure_user(db, m); w = db.scalar(select(Wallet).where(Wallet.user_id == u.id))
        await m.answer(f"نام: {u.full_name}\nآیدی: {u.telegram_id}\nموبایل: {u.phone or '-'}\nموجودی: {w.balance} تومان")
    finally: db.close()


async def wallet(m: Message):
    db = SessionLocal();
    try:
        u = ensure_user(db, m); w = db.scalar(select(Wallet).where(Wallet.user_id == u.id))
        await m.answer(f"کیف پول شما: {w.balance} تومان\nبرای شارژ، پیام را با فرمت زیر بفرستید:\nشارژ 50000")
    finally: db.close()


async def buy(m: Message):
    db = SessionLocal();
    try:
        ps = db.scalars(select(Product).where(Product.is_active == True)).all()
        if not ps: return await m.answer("محصول فعالی موجود نیست.")
        txt = "برای خرید، کد را ارسال کنید: خرید <شناسه>\n\n" + "\n".join([f"{p.id}) {p.title} | {p.price} تومان" for p in ps])
        await m.answer(txt)
    finally: db.close()


async def renew(m: Message):
    db = SessionLocal();
    try:
        u = ensure_user(db, m)
        sv = db.scalars(select(VpnService).where(VpnService.user_id == u.id)).all()
        if not sv: return await m.answer('سرویسی برای تمدید ندارید.')
        await m.answer("برای تمدید با پشتیبانی هماهنگ کنید یا دستور: تمدید <service_id>")
    finally: db.close()


async def services(m: Message):
    db = SessionLocal();
    try:
        u = ensure_user(db, m)
        sv = db.scalars(select(VpnService).where(VpnService.user_id == u.id)).all()
        if not sv: return await m.answer('سرویسی ندارید.')
        txt = "سرویس‌های شما:\n" + "\n".join([f"{s.id}) {s.client_email} | {s.status} | پایان: {s.expires_at}" for s in sv])
        txt += "\nبرای دریافت لینک: کانفیگ <service_id>"
        await m.answer(txt)
    finally: db.close()


async def tutorials(m: Message):
    db = SessionLocal();
    try:
        rows = db.scalars(select(Tutorial).limit(10)).all()
        await m.answer("\n\n".join([f"{r.title}\n{r.content}" for r in rows]) or "آموزشی ثبت نشده است.")
    finally: db.close()


async def apps(m: Message):
    db = SessionLocal();
    try:
        rows = db.scalars(select(AppDownload)).all()
        await m.answer("\n".join([f"{a.platform}: {a.url}" for a in rows]) or "لینکی ثبت نشده است.")
    finally: db.close()


async def ticket(m: Message):
    db = SessionLocal();
    try:
        u = ensure_user(db, m)
        t = Ticket(user_id=u.id, title="تیکت جدید")
        db.add(t); db.commit(); db.refresh(t)
        db.add(TicketMessage(ticket_id=t.id, sender_type='user', body='درخواست پشتیبانی')); db.commit()
        await m.answer(f"تیکت ثبت شد: #{t.id}")
    finally: db.close()


async def text_commands(m: Message):
    db = SessionLocal();
    try:
        u = ensure_user(db, m)
        t = m.text.strip()
        if t.startswith('خرید '):
            pid = int(t.split()[1]); p = db.get(Product, pid)
            if not p: return await m.answer('محصول نامعتبر است.')
            o = Order(order_code=f"ORD-{u.id}-{int(asyncio.get_event_loop().time())}", user_id=u.id, product_id=p.id, amount=p.price)
            db.add(o); db.commit(); db.refresh(o)
            pay = Payment(order_id=o.id, user_id=u.id, amount=p.price, method='card_to_card')
            db.add(pay); db.commit(); db.refresh(pay)
            await m.answer(f"سفارش {o.order_code} ساخته شد.\nمبلغ: {p.price}\nشماره کارت: {settings.card_number}\nنام دارنده: {settings.card_holder_name}\nرسید را با فرمت زیر بفرستید:\nرسید {pay.id} <file_id>")
        elif t.startswith('شارژ '):
            amt = float(t.split()[1]); pay = Payment(user_id=u.id, amount=amt, method='card_to_card')
            db.add(pay); db.commit(); db.refresh(pay)
            await m.answer(f"درخواست شارژ ثبت شد.\nمبلغ: {amt}\nشماره کارت: {settings.card_number}\nکپی مبلغ: {amt}\nکپی کارت: {settings.card_number}\nارسال رسید: رسید {pay.id} <file_id>")
        elif t.startswith('رسید '):
            _, pid, fid = t.split(maxsplit=2)
            db.add(Receipt(payment_id=int(pid), telegram_file_id=fid, status='pending')); db.commit(); await m.answer('رسید ثبت شد و در انتظار تایید ادمین است.')
        elif t.startswith('کانفیگ '):
            sid = int(t.split()[1]); s = db.get(VpnService, sid)
            if not s or s.user_id != u.id: return await m.answer('سرویس یافت نشد.')
            await m.answer(f"کانفیگ: vmess://{s.client_email}\nSubscription: sub://{s.sub_id or s.client_id}\n(خروجی QR از پنل وب/API)")
        elif t.startswith('ادمین تایید '):
            if not db.scalar(select(Admin).where(Admin.telegram_id == m.from_user.id)): return
            pid = int(t.split()[2]); p = db.get(Payment, pid); p.status = 'approved'
            if p.order_id: db.get(Order, p.order_id).status = 'paid'
            else:
                w = db.scalar(select(Wallet).where(Wallet.user_id == p.user_id)); w.balance = float(w.balance) + float(p.amount)
            db.commit(); await m.answer('تایید شد.')
    finally: db.close()


async def admin_menu(m: Message):
    db = SessionLocal();
    try:
        if not db.scalar(select(Admin).where(Admin.telegram_id == m.from_user.id)): return await m.answer('دسترسی ندارید.')
        await m.answer('پنل ادمین:\n- ادمین تایید <payment_id>\n- مشاهده پرداخت‌های در انتظار از API')
    finally: db.close()


async def run_bot():
    bot = Bot(settings.bot_token)
    dp = Dispatcher()
    dp.message.register(start, CommandStart())
    dp.message.register(profile, F.text == "👤 پروفایل")
    dp.message.register(wallet, F.text == "💼 کیف پول")
    dp.message.register(buy, F.text == "🛒 خرید VPN")
    dp.message.register(renew, F.text == "🔄 تمدید VPN")
    dp.message.register(services, F.text == "📦 سرویس‌های من")
    dp.message.register(tutorials, F.text == "🎓 آموزش‌ها")
    dp.message.register(apps, F.text == "📲 اپ‌ها")
    dp.message.register(ticket, F.text == "🎫 ثبت تیکت")
    dp.message.register(admin_menu, F.text == "🛠 پنل ادمین")
    dp.message.register(text_commands)
    await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(run_bot())
