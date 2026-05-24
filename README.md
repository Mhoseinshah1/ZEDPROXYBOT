# ZEDPROXYBOT - فاز اول

## امکانات فعلی فاز اول
- ربات تلگرام aiogram 3 با منوی فارسی: شروع، پروفایل، کیف پول، خرید، ثبت تیکت.
- API مدیریت FastAPI با ورود ادمین JWT و داشبورد.
- مدل‌های اصلی دیتابیس برای کاربران، کیف پول، سفارش، پرداخت، VPN، تیکت، گزارش.
- آداپتر پنل سنایی 3x-ui با endpointهای `/login` و `/panel/api/inbounds/*`.
- Docker Compose شامل app, bot, db, redis, nginx.
- نصب تعاملی Ubuntu 24 با `install.sh`.

## اجرا
```bash
cp .env.example .env
docker compose up -d --build
```

## نصب یک‌خطی
```bash
bash <(curl -Ls https://example.com/install.sh)
```

## ورود پنل مدیریت
1) با اطلاعات ادمین اولیه (`main_admin / admin123`) لاگین API بگیرید:
```bash
curl -X POST http://SERVER/api/admin/login -F 'username=main_admin' -F 'password=admin123'
```
2) توکن را روی endpointها بزنید.

## افزودن پنل 3x-ui
از API مدیریت رکورد `vpn_panels` بسازید و سپس:
```bash
POST /api/admin/panels/{panel_id}/test
```

## بکاپ و ری‌استور
```bash
./scripts/backup.sh
./scripts/restore.sh backups/FILE.sql
```

## آپدیت
```bash
./scripts/update.sh
```

## Chat ID گروه گزارشات
ربات را در گروه ادمین کنید و از ربات‌هایی مثل `@userinfobot` برای دریافت chat id (معمولاً با `-100`) استفاده کنید.
