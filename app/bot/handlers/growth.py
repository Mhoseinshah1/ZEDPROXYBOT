import random
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select, func
from app.db.session import SessionLocal
from app.models.entities import User, Wallet, WalletTransaction, Product, Order, WheelPrize, WheelSpin, ResellerRequest, ReferralCommission
from app.services.vpn.provisioning import provision_paid_order

router = Router()


def _user(db, telegram_id: int):
    return db.scalar(select(User).where(User.telegram_id == telegram_id))


@router.message(F.text == 'اشتراک رایگان {تست}')
async def free_trial(message: Message):
    db = SessionLocal()
    try:
        user = _user(db, message.from_user.id)
        used = db.scalar(select(func.count(Order.id)).where(Order.user_id == user.id, Order.order_type == 'trial'))
        if used:
            return await message.answer('شما قبلاً از اشتراک تست رایگان استفاده کرده‌اید.')
        plan = db.scalar(select(Product).where(Product.is_active == True, Product.is_test_plan == True).order_by(Product.sort_order, Product.id))
        if not plan or not plan.inbound_id:
            return await message.answer('پلن تست رایگان هنوز توسط مدیریت تنظیم نشده است.')
        order = Order(order_code=f'TRL-{user.id}-{int(datetime.utcnow().timestamp())}', user_id=user.id, product_id=plan.id, amount=0, status='paid', order_type='trial')
        db.add(order); db.commit(); db.refresh(order)
        try:
            await provision_paid_order(order.id, db, bot=message.bot)
            await message.answer('اشتراک تست ساخته شد و لینک برای شما ارسال شد.')
        except Exception as exc:
            order.status = 'provision_failed'; db.commit()
            await message.answer(f'ساخت تست رایگان با خطا روبه‌رو شد: {exc}')
    finally:
        db.close()


@router.message(F.text == '👥 زیر مجموعه گیری')
async def referral(message: Message):
    db = SessionLocal()
    try:
        user = _user(db, message.from_user.id)
        if not user.referral_code:
            user.referral_code = f'R{user.telegram_id}'
            db.commit()
        children = db.scalars(select(User).where(User.referred_by_user_id == user.id)).all()
        commission = db.scalar(select(func.coalesce(func.sum(ReferralCommission.amount), 0)).where(ReferralCommission.referrer_user_id == user.id))
        bot_info = await message.bot.get_me()
        link = f'https://t.me/{bot_info.username}?start={user.referral_code}'
        await message.answer(f'لینک دعوت شما:\n{link}\n\nتعداد زیرمجموعه‌ها: {len(children)}\nمجموع پورسانت: {commission} تومان')
    finally:
        db.close()


@router.message(F.text == '🎲 گردونه شانس')
async def wheel(message: Message):
    db = SessionLocal()
    try:
        prizes = db.scalars(select(WheelPrize).where(WheelPrize.is_active == True)).all()
        if not prizes:
            return await message.answer('گردونه شانس هنوز توسط مدیریت فعال نشده است.')
        prize = random.choices(prizes, weights=[max(p.probability, 0.01) for p in prizes], k=1)[0]
        user = _user(db, message.from_user.id)
        result = prize.title
        if prize.prize_type == 'wallet_amount' and prize.prize_value > 0:
            wallet = db.scalar(select(Wallet).where(Wallet.user_id == user.id))
            wallet.balance = float(wallet.balance) + float(prize.prize_value)
            db.add(WalletTransaction(user_id=user.id, amount=prize.prize_value, tx_type='wheel_prize', status='approved', meta={'prize_id': prize.id}))
            result = f'{prize.title} - {prize.prize_value} تومان به کیف پول شما اضافه شد.'
        db.add(WheelSpin(user_id=user.id, prize_id=prize.id, result_text=result)); db.commit()
        await message.answer(f'🎉 نتیجه گردونه:\n{result}')
    finally:
        db.close()


@router.message(F.text == 'درخواست نمایندگی')
async def reseller_request(message: Message):
    db = SessionLocal()
    try:
        user = _user(db, message.from_user.id)
        existing = db.scalar(select(ResellerRequest).where(ResellerRequest.user_id == user.id, ResellerRequest.status == 'pending'))
        if existing:
            return await message.answer('درخواست نمایندگی شما قبلاً ثبت شده و در انتظار بررسی است.')
        req = ResellerRequest(user_id=user.id, name=user.full_name or '-', phone=user.phone or '-', sales_estimate='ثبت اولیه از ربات', description='کاربر از منوی درخواست نمایندگی اقدام کرد.', status='pending')
        db.add(req); db.commit()
        await message.answer('درخواست نمایندگی شما ثبت شد. تیم مدیریت بررسی خواهد کرد.')
    finally:
        db.close()
