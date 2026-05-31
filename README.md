# ZEDPROXYBOT

## نصب با یک دستور (Ubuntu 24)
```bash
bash <(curl -Ls https://raw.githubusercontent.com/Mhoseinshah1/ZEDPROXYBOT-v2/main/install.sh)
```

اسکریپت منوی مدیریت می‌دهد:
1) نصب ربات
2) آپدیت ربات
3) حذف ربات
4) بکاپ دیتابیس
5) ری‌استور دیتابیس
6) ری‌استارت سرویس‌ها
7) وضعیت سرویس‌ها
8) لاگ bot
9) لاگ app
10) خروج

## مسیرها
- مسیر نصب: `/opt/zedproxybot`
- مسیر بکاپ‌ها: `/opt/zedproxybot/backups`

## آپدیت بعد از merge
بعد از هر merge روی branch `main` فقط همین دستور را بزنید:
```bash
bash <(curl -Ls https://raw.githubusercontent.com/Mhoseinshah1/ZEDPROXYBOT-v2/main/install.sh)
```
سپس گزینه `2) آپدیت ربات` را انتخاب کنید.

## رفتار گزینه‌ها
- **نصب**: پیش‌نیازها را نصب می‌کند، پروژه را clone می‌کند، `.env` می‌سازد، سرویس‌ها را بالا می‌آورد، migration/seed اجرا می‌کند.
- **آپدیت**: قبل از آپدیت بکاپ می‌گیرد، `git pull` می‌زند، build/up انجام می‌دهد، migration و restart اجرا می‌کند.
- **حذف**: با تأیید کاربر انجام می‌شود، امکان حذف volume و حذف مسیر پروژه را جداگانه می‌پرسد.
- **بکاپ/ری‌استور**: لیست فایل‌های بکاپ و ری‌استور تعاملی.
- **لاگ‌ها**: مشاهده لاگ `app` و `bot` با حالت follow.

## خطاهای رایج
- اگر Docker نصب نبود: اسکریپت تلاش می‌کند نصب کند.
- اگر `git pull` شکست خورد: پیام خطای واضح نمایش می‌دهد و ادامه نمی‌دهد.
- اگر `.env` از قبل وجود داشته باشد: در آپدیت بازنویسی نمی‌شود.
- اگر health check ناموفق باشد: هشدار می‌دهد تا لاگ‌ها بررسی شوند.

## تست وضعیت
```bash
cd /opt/zedproxybot
docker compose ps || docker-compose ps
curl http://127.0.0.1:8000/health
```


## Financial settings (after install)
- Card number and card holder are **not** asked in installer.
- After install, configure from bot admin panel:
  `🛠 پنل ادمین → ⚙️ تنظیمات → 💳 تنظیمات مالی`
- Then set card number, card holder, and enable card-to-card.


## Installer notes
- Installer menu is English.
- Installer asks only technical values (token/admin/domain/db/redis/report chat).
- Card number and card holder are **not** asked during install.
- Configure financial settings later in bot: `🛠 پنل ادمین → ⚙️ تنظیمات → 💳 تنظیمات مالی`.
