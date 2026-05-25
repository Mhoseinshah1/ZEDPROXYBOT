# ZEDPROXYBOT

## اجرای سریع
```bash
cp .env.example .env
docker compose down
docker compose up -d --build
docker compose ps
curl http://127.0.0.1:8000/health
```

## تنظیم ادمین اصلی
- در `.env` مقدار `MAIN_ADMIN_ID` را با آیدی عددی تلگرام خود پر کنید.
- `ADMIN_PASSWORD` را هم تعیین کنید.
- با `/start` اگر آیدی شما برابر `MAIN_ADMIN_ID` باشد، خودکار به عنوان owner ثبت می‌شوید.

## تست ربات (مرحله‌به‌مرحله)
1. `/start` بزنید و منوی فارسی را ببینید.
2. اگر ادمین هستید، دکمه `🛠 پنل ادمین` باید نمایش داده شود.
3. از `🛒 خرید VPN` یک محصول انتخاب و خرید ثبت کنید.
4. پیام پرداخت می‌گیرید؛ رسید را عکس/فایل با کپشن `receipt <payment_id>` ارسال کنید.
5. با اکانت ادمین وارد `🛠 پنل ادمین` > `🧾 پرداخت‌های در انتظار` شوید.
6. با دکمه inline پرداخت را تایید/رد کنید.
7. در تایید سفارش VPN، provisioning اجرا می‌شود و لینک/QR برای کاربر ارسال می‌شود.

## لاگ‌ها
```bash
docker compose logs --tail=100 app
docker compose logs --tail=100 bot
```

## عملیات
```bash
./scripts/backup.sh
./scripts/restore.sh backups/<file>.sql
./scripts/update.sh
```
