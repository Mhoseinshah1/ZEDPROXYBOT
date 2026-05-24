"""initial schema full

Revision ID: 0001
Revises:
Create Date: 2026-05-24
"""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('users', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('telegram_id', sa.BigInteger(), unique=True), sa.Column('username', sa.String(64)), sa.Column('full_name', sa.String(128)), sa.Column('phone', sa.String(24)), sa.Column('is_blocked', sa.Boolean(), server_default=sa.text('false')), sa.Column('created_at', sa.DateTime()))
    op.create_table('wallets', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), unique=True), sa.Column('balance', sa.Numeric(14,2)))
    op.create_table('wallet_transactions', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')), sa.Column('amount', sa.Numeric(14,2)), sa.Column('tx_type', sa.String(32)), sa.Column('status', sa.String(32)), sa.Column('meta', sa.JSON()), sa.Column('created_at', sa.DateTime()))
    op.create_table('vpn_panels', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('name', sa.String(64), unique=True), sa.Column('host', sa.String(255)), sa.Column('port', sa.Integer()), sa.Column('base_path', sa.String(64)), sa.Column('username', sa.String(64)), sa.Column('password', sa.String(128)), sa.Column('location', sa.String(128)), sa.Column('is_active', sa.Boolean()))
    op.create_table('vpn_inbounds', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('panel_id', sa.Integer(), sa.ForeignKey('vpn_panels.id')), sa.Column('inbound_remote_id', sa.Integer()), sa.Column('remark', sa.String(128)), sa.Column('protocol', sa.String(24)))
    op.create_table('products', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('title', sa.String(128)), sa.Column('price', sa.Numeric(14,2)), sa.Column('days', sa.Integer()), sa.Column('traffic_gb', sa.Integer()), sa.Column('inbound_id', sa.Integer(), sa.ForeignKey('vpn_inbounds.id')), sa.Column('is_active', sa.Boolean()))
    op.create_table('orders', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('order_code', sa.String(32), unique=True), sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')), sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id')), sa.Column('amount', sa.Numeric(14,2)), sa.Column('status', sa.String(24)), sa.Column('note', sa.Text()), sa.Column('created_at', sa.DateTime()))
    op.create_table('payments', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('order_id', sa.Integer(), sa.ForeignKey('orders.id')), sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')), sa.Column('amount', sa.Numeric(14,2)), sa.Column('method', sa.String(32)), sa.Column('status', sa.String(32)), sa.Column('created_at', sa.DateTime()))
    op.create_table('receipts', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('payment_id', sa.Integer(), sa.ForeignKey('payments.id')), sa.Column('telegram_file_id', sa.String(255)), sa.Column('status', sa.String(16)))
    op.create_table('vpn_services', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')), sa.Column('order_id', sa.Integer(), sa.ForeignKey('orders.id')), sa.Column('inbound_id', sa.Integer(), sa.ForeignKey('vpn_inbounds.id')), sa.Column('client_id', sa.String(64), unique=True), sa.Column('client_email', sa.String(128), unique=True), sa.Column('sub_id', sa.String(64)), sa.Column('status', sa.String(24)), sa.Column('expires_at', sa.DateTime()), sa.Column('total_gb', sa.Integer()), sa.Column('note', sa.Text()))
    op.create_table('tickets', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')), sa.Column('title', sa.String(128)), sa.Column('category', sa.String(32)), sa.Column('status', sa.String(16)))
    op.create_table('ticket_messages', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('ticket_id', sa.Integer(), sa.ForeignKey('tickets.id')), sa.Column('sender_type', sa.String(16)), sa.Column('body', sa.Text()), sa.Column('created_at', sa.DateTime()))
    op.create_table('tutorials', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('title', sa.String(128)), sa.Column('category', sa.String(64)), sa.Column('content', sa.Text()))
    op.create_table('app_downloads', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('platform', sa.String(16), unique=True), sa.Column('url', sa.String(1024)))
    op.create_table('bot_texts', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('key', sa.String(64), unique=True), sa.Column('value', sa.Text()))
    op.create_table('settings', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('key', sa.String(64), unique=True), sa.Column('value', sa.Text()))
    op.create_table('admins', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('telegram_id', sa.BigInteger(), unique=True), sa.Column('username', sa.String(64)), sa.Column('password_hash', sa.String(255)), sa.Column('role', sa.String(16)), sa.Column('is_active', sa.Boolean()))
    op.create_table('report_logs', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('event_type', sa.String(64)), sa.Column('level', sa.String(16)), sa.Column('payload', sa.JSON()), sa.Column('created_at', sa.DateTime()))
    op.create_table('audit_logs', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('admin_id', sa.Integer(), sa.ForeignKey('admins.id')), sa.Column('action', sa.String(64)), sa.Column('payload', sa.JSON()), sa.Column('created_at', sa.DateTime()))

def downgrade():
    for t in ['audit_logs','report_logs','admins','settings','bot_texts','app_downloads','tutorials','ticket_messages','tickets','vpn_services','receipts','payments','orders','products','vpn_inbounds','vpn_panels','wallet_transactions','wallets','users']:
        op.drop_table(t)
