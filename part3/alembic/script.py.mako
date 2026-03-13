<%!
from alembic.autogenerate import renderers
%>
"""Auto-generated Alembic script."""
revision = '${up_revision}'
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}

from alembic import op
import sqlalchemy as sa

def upgrade():
    ${upgrades if upgrades.strip() else "pass"}

def downgrade():
    ${downgrades if downgrades.strip() else "pass"}
