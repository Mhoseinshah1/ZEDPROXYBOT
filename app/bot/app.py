import asyncio
from aiogram import Bot, Dispatcher
from app.core.config import settings
from app.bot.handlers import start, profile, wallet, products, orders, payments, vpn_services, tickets, tutorials, growth
from app.bot.handlers.admin import dashboard as admin_dashboard, payments as admin_payments


async def run_bot():
    bot = Bot(settings.bot_token)
    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(wallet.router)
    dp.include_router(products.router)
    dp.include_router(orders.router)
    dp.include_router(payments.router)
    dp.include_router(vpn_services.router)
    dp.include_router(tickets.router)
    dp.include_router(tutorials.router)
    dp.include_router(growth.router)
    dp.include_router(admin_dashboard.router)
    dp.include_router(admin_payments.router)

    if not settings.use_webhook:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    else:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(run_bot())
