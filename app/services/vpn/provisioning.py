import uuid
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session
from aiogram import Bot
from aiogram.types import BufferedInputFile
from app.models.entities import Order, Product, VpnInbound, VpnPanel, VpnService, User
from app.services.vpn.adapters.sanaei_3xui import Sanaei3xUiAdapter, SanaeiApiError
from app.services.reports.service import ReportService


async def provision_paid_order(order_id: int, db: Session, bot: Bot | None = None, report_service: ReportService | None = None):
    order = db.get(Order, order_id)
    if not order:
        raise ValueError("order_not_found")
    product = db.get(Product, order.product_id)
    inbound = db.get(VpnInbound, product.inbound_id) if product and product.inbound_id else None
    if not product or not inbound:
        raise ValueError("product_or_inbound_missing")
    panel = db.get(VpnPanel, inbound.panel_id)
    if not panel:
        raise ValueError("panel_not_found")
    user = db.get(User, order.user_id)

    email = f"u{user.telegram_id}_{uuid.uuid4().hex[:8]}"
    sub_id = uuid.uuid4().hex[:16]
    expiry = datetime.utcnow() + timedelta(days=product.days)
    total_bytes = int(product.traffic_gb) * 1024 * 1024 * 1024
    client = {
        "id": str(uuid.uuid4()),
        "email": email,
        "enable": True,
        "tgId": str(user.telegram_id),
        "subId": sub_id,
        "expiryTime": int(expiry.timestamp() * 1000),
        "totalGB": total_bytes,
        "limitIp": 0,
    }
    adapter = Sanaei3xUiAdapter(panel.host, panel.port, panel.username, panel.password, panel.base_path)
    try:
        await adapter.create_client(inbound.inbound_remote_id, client)
        sub_link = await adapter.get_subscription_link(sub_id)
        config_link = await adapter.get_config_link(inbound.inbound_remote_id, email)
    except SanaeiApiError as e:
        if report_service:
            await report_service.emit("vpn_provision_failed", f"🔴 خطای ساخت سرویس VPN\nOrder:{order.order_code}\n{str(e)}", {"order_id": order.id, "error": str(e)}, level="error")
        raise

    svc = VpnService(
        user_id=user.id,
        order_id=order.id,
        inbound_id=inbound.id,
        client_id=client["id"],
        client_email=email,
        sub_id=sub_id,
        status="active",
        expires_at=expiry,
        total_gb=product.traffic_gb,
    )
    db.add(svc)
    order.status = "paid"
    db.commit()

    link = sub_link or config_link
    if bot:
        await bot.send_message(user.telegram_id, f"✅ سرویس شما فعال شد\nلینک اشتراک:\n{link}")
        qr = Sanaei3xUiAdapter.qrcode_png_bytes(link)
        await bot.send_photo(user.telegram_id, photo=BufferedInputFile(qr, filename="subscription.png"))
    if report_service:
        await report_service.emit("vpn_service_created", f"🟢 سرویس VPN ساخته شد\nOrder:{order.order_code}", {"order_id": order.id, "user_id": user.id, "service_email": email})
    return {"service_id": svc.id, "subscription_link": sub_link, "config_link": config_link}
