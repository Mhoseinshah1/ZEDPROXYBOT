# ZedProxyBot - فاز اول

این پروژه یک زیرساخت production-ready برای فروش اشتراک VPN با ربات تلگرام فارسی است.

## معماری فاز اول
- Bot (aiogram3)
- API/Admin Backend (FastAPI)
- PostgreSQL + Redis
- Adapter ماژولار برای 3x-ui
- گزارش event-based + گروه گزارشات تلگرام
- پرداخت کارت‌به‌کارت + کیف پول داخلی

## اجرای سریع
```bash
cp .env.example .env
docker compose up -d --build
```

## نصب Ubuntu 24 با یک دستور
```bash
bash <(curl -Ls https://example.com/install.sh)
```

## اسکریپت‌ها
- `scripts/backup.sh`
- `scripts/restore.sh <file.sql>`
- `scripts/update.sh`

## 3x-ui
آداپتور بر اساس endpoint رسمی `/login` و `/panel/api/inbounds/*` نوشته شده تا با نسخه رسمی MHSanaei/3x-ui سازگار باشد.

## فازهای بعدی
ساختار در `services/payment/adapters` و `services/vpn/adapters` برای افزودن درگاه‌های جدید، Telegram Stars، Crypto و سایر امکانات آماده شده است.
