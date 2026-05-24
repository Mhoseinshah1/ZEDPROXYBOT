from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.db.init_db import init_db
from app.models.entities import *
from app.services.vpn.adapters.sanaei_3xui import Sanaei3xUiAdapter, SanaeiApiError

app = FastAPI(title="ZedProxyBot API")
security = HTTPBearer()
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.on_event("startup")
def boot(): init_db()

def admin_auth(c: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try: payload = jwt.decode(c.credentials, settings.jwt_secret, algorithms=["HS256"])
    except Exception: raise HTTPException(401, "توکن نامعتبر")
    admin = db.scalar(select(Admin).where(Admin.id == int(payload["sub"]), Admin.is_active == True))
    if not admin: raise HTTPException(401, "عدم دسترسی")
    return admin

def audit(db: Session, admin_id: int, action: str, payload: dict | None = None):
    db.add(AuditLog(admin_id=admin_id, action=action, payload=payload or {})); db.commit()

@app.get('/health')
def health(): return {'ok': True, 'time': datetime.utcnow()}

@app.post('/api/admin/login')
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    admin = db.scalar(select(Admin).where(Admin.username == username))
    if not admin or not pwd.verify(password, admin.password_hash): raise HTTPException(400, "نام کاربری یا رمز اشتباه است")
    token = jwt.encode({'sub': str(admin.id), 'exp': datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)}, settings.jwt_secret, algorithm='HS256')
    return {'access_token': token}

@app.get('/api/admin/dashboard')
def dashboard(_: Admin = Depends(admin_auth), db: Session = Depends(get_db)):
    return {'users': db.scalar(select(func.count(User.id))), 'orders': db.scalar(select(func.count(Order.id))), 'pending_payments': db.scalar(select(func.count(Payment.id)).where(Payment.status == 'pending')), 'open_tickets': db.scalar(select(func.count(Ticket.id)).where(Ticket.status == 'open'))}

@app.get('/api/admin/users')
def users(_: Admin = Depends(admin_auth), db: Session = Depends(get_db)):
    return [{'id': u.id,'telegram_id':u.telegram_id,'name':u.full_name,'phone':u.phone,'blocked':u.is_blocked} for u in db.scalars(select(User).order_by(User.id.desc()).limit(200)).all()]

@app.post('/api/admin/users/{user_id}/block')
def block_user(user_id: int, blocked: bool = Form(...), admin: Admin = Depends(admin_auth), db: Session = Depends(get_db)):
    u = db.get(User, user_id); 
    if not u: raise HTTPException(404, 'کاربر یافت نشد')
    u.is_blocked = blocked; db.commit(); audit(db, admin.id, 'block_user', {'user_id': user_id, 'blocked': blocked}); return {'ok': True}

@app.get('/api/admin/products')
def products(_: Admin = Depends(admin_auth), db: Session = Depends(get_db)):
    return [vars(p) for p in db.scalars(select(Product)).all()]

@app.get('/api/admin/orders')
def orders(_: Admin = Depends(admin_auth), db: Session = Depends(get_db)):
    return [vars(o) for o in db.scalars(select(Order).order_by(Order.id.desc()).limit(200)).all()]

@app.get('/api/admin/payments')
def payments(_: Admin = Depends(admin_auth), db: Session = Depends(get_db)):
    return [vars(p) for p in db.scalars(select(Payment).order_by(Payment.id.desc()).limit(200)).all()]

@app.post('/api/admin/payments/{payment_id}/decision')
def payment_decision(payment_id: int, status: str = Form(...), admin: Admin = Depends(admin_auth), db: Session = Depends(get_db)):
    p = db.get(Payment, payment_id)
    if not p: raise HTTPException(404, 'پرداخت یافت نشد')
    if status not in ['approved', 'rejected']: raise HTTPException(400, 'وضعیت نامعتبر')
    p.status = status
    if p.order_id:
        o = db.get(Order, p.order_id); o.status = 'paid' if status == 'approved' else 'payment_rejected'
    else:
        w = db.scalar(select(Wallet).where(Wallet.user_id == p.user_id)); w.balance = float(w.balance) + float(p.amount) if status == 'approved' else w.balance
        db.add(WalletTransaction(user_id=p.user_id, amount=p.amount, tx_type='topup', status=status, meta={'payment_id': p.id}))
    db.commit(); audit(db, admin.id, 'payment_decision', {'payment_id': payment_id, 'status': status}); return {'ok': True}

@app.get('/api/admin/vpn-services')
def vpn_services(_: Admin = Depends(admin_auth), db: Session = Depends(get_db)):
    return [vars(s) for s in db.scalars(select(VpnService).order_by(VpnService.id.desc())).all()]

@app.get('/api/admin/tickets')
def tickets(_: Admin = Depends(admin_auth), db: Session = Depends(get_db)):
    return [vars(t) for t in db.scalars(select(Ticket).order_by(Ticket.id.desc()).limit(200)).all()]

@app.get('/api/admin/reports')
def reports(_: Admin = Depends(admin_auth), db: Session = Depends(get_db)):
    return [vars(r) for r in db.scalars(select(ReportLog).order_by(ReportLog.id.desc()).limit(200)).all()]

@app.get('/api/admin/settings')
def settings_list(_: Admin = Depends(admin_auth), db: Session = Depends(get_db)):
    return [{'key': s.key, 'value': s.value} for s in db.scalars(select(Setting)).all()]

@app.post('/api/admin/settings')
def settings_set(key: str = Form(...), value: str = Form(...), admin: Admin = Depends(admin_auth), db: Session = Depends(get_db)):
    s = db.scalar(select(Setting).where(Setting.key == key))
    if not s: s = Setting(key=key, value=value); db.add(s)
    else: s.value = value
    db.commit(); audit(db, admin.id, 'setting_update', {'key': key}); return {'ok': True}

@app.post('/api/admin/panels/{panel_id}/test')
async def panel_test(panel_id: int, _: Admin = Depends(admin_auth), db: Session = Depends(get_db)):
    p = db.get(VpnPanel, panel_id)
    if not p: raise HTTPException(404, 'panel not found')
    ad = Sanaei3xUiAdapter(p.host, p.port, p.username, p.password, p.base_path)
    try: return await ad.test_connection()
    except SanaeiApiError as e: raise HTTPException(400, str(e))

@app.get('/admin', response_class=HTMLResponse)
def admin_page():
    return """<html lang='fa' dir='rtl'><body><h2>پنل مدیریت ساده</h2><p>/api/admin/login</p><ul><li>dashboard</li><li>users</li><li>orders</li><li>payments</li><li>products</li><li>vpn-services</li><li>tickets</li><li>reports</li><li>settings</li></ul></body></html>"""
