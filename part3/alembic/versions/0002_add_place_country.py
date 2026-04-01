"""add country column to places

Revision ID: 0002_add_place_country
Revises: 0001_initial
Create Date: 2026-03-31 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_add_place_country"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("places")}
    if "country" not in columns:
        op.add_column("places", sa.Column("country", sa.String(), nullable=True))


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("places")}
    if "country" in columns:
        op.drop_column("places", "country")
