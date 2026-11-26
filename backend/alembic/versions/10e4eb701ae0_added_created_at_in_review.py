"""added created_at in review

Revision ID: 10e4eb701ae0
Revises: c3e5a7b9d014
Create Date: 2026-11-25 20:26:45.746731

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "10e4eb701ae0"
down_revision: Union[str, Sequence[str], None] = "c3e5a7b9d014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "reviews",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("reviews", "created_at")
