from sqlalchemy import String, BigInteger, Boolean, Integer, ForeignKey, Numeric, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(64))
    full_name: Mapped[str] = mapped_column(String(128))
    mobile: Mapped[str | None] = mapped_column(String(32))
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    wallet_balance: Mapped[float] = mapped_column(Numeric(14, 2), default=0)


class VpnPanel(Base, TimestampMixin):
    __tablename__ = "vpn_panels"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    base_url: Mapped[str] = mapped_column(String(255))
    username: Mapped[str] = mapped_column(String(64))
    password: Mapped[str] = mapped_column(String(255))
    location: Mapped[str | None] = mapped_column(String(128))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    description: Mapped[str | None] = mapped_column(Text)


class VpnInbound(Base, TimestampMixin):
    __tablename__ = "vpn_inbounds"
    id: Mapped[int] = mapped_column(primary_key=True)
    panel_id: Mapped[int] = mapped_column(ForeignKey("vpn_panels.id"), index=True)
    inbound_id: Mapped[int] = mapped_column(index=True)
    remark: Mapped[str] = mapped_column(String(128))
    protocol: Mapped[str] = mapped_column(String(32))
    raw_payload: Mapped[dict] = mapped_column(JSON)


class Product(Base, TimestampMixin):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(128))
    price: Mapped[float] = mapped_column(Numeric(14, 2))
    period_days: Mapped[int] = mapped_column(Integer)
    traffic_gb: Mapped[int] = mapped_column(Integer)
    inbound_ref_id: Mapped[int] = mapped_column(ForeignKey("vpn_inbounds.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
