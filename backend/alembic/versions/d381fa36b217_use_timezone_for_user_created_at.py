"""Use timezone-aware timestamps for users.

Revision ID: d381fa36b217
Revises: 5b207c6fa21e
Create Date: 2026-11-12 00:10:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d381fa36b217"
down_revision: Union[str, Sequence[str], None] = "5b207c6fa21e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "created_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        postgresql_using="created_at AT TIME ZONE current_setting('TIMEZONE')",
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        postgresql_using="created_at AT TIME ZONE current_setting('TIMEZONE')",
    )
