"""Create book table

Revision ID: 8bb5f8f2d2d1
Revises: 621cac40cba6
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8bb5f8f2d2d1"
down_revision: Union[str, Sequence[str], None] = "621cac40cba6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("isbn", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("isbn"),
    )


def downgrade() -> None:
    op.drop_table("books")
