"""initial migration

Revision ID: 0001_initial
Revises: 
Create Date: 2026-03-13 00:00:00.000000
"""

from alembic import op


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create all tables defined in the ORM models
    from hbnb.persistence.models import Base

    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade():
    from hbnb.persistence.models import Base

    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
