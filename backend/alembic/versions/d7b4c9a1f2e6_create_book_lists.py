"""Create persistent book lists and book associations.

Revision ID: d7b4c9a1f2e6
Revises: 3a91c6e2d704
Create Date: 2026-11-26 17:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d7b4c9a1f2e6"
down_revision: Union[str, Sequence[str], None] = "3a91c6e2d704"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "book_lists",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("private", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_book_lists_owner_id", "book_lists", ["owner_id"])

    op.create_table(
        "book_list_books",
        sa.Column("book_list_id", sa.Integer(), nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["book_list_id"], ["book_lists.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("book_list_id", "book_id"),
    )


def downgrade() -> None:
    op.drop_table("book_list_books")
    op.drop_index("ix_book_lists_owner_id", table_name="book_lists")
    op.drop_table("book_lists")
