"""initial schema

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
    op.create_table('users', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('telegram_id', sa.BigInteger(), unique=True), sa.Column('username', sa.String(64)), sa.Column('full_name', sa.String(128)), sa.Column('phone', sa.String(24)), sa.Column('is_blocked', sa.Boolean(), server_default='false'), sa.Column('created_at', sa.DateTime()))

def downgrade():
    op.drop_table('users')
