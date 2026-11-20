"""Add isSpoiler to reviews.

Revision ID: c20b7e7bd31f
Revises: b6263a817e79
Create Date: 2026-11-20 11:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c20b7e7bd31f"
down_revision: Union[str, Sequence[str], None] = "b6263a817e79"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "reviews",
        sa.Column("isSpoiler", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("reviews", "isSpoiler", server_default=None)


def downgrade() -> None:
    op.drop_column("reviews", "isSpoiler")
