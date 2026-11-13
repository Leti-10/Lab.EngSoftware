"""create reports table

Revision ID: 5b207c6fa21e
Revises: 9cd1e27391de
Create Date: 2026-10-17 09:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "5b207c6fa21e"
down_revision: Union[str, Sequence[str], None] = "a74c620a1fbe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "reports",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column("target_entity", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "target_entity",
            "target_id",
            name="uq_reports_user_target",
        ),
    )


def downgrade() -> None:
    op.drop_table("reports")
