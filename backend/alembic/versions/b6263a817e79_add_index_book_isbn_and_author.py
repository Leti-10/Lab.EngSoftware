"""add index book isbn and author

Revision ID: b6263a817e79
Revises: d381fa36b217
Create Date: 2026-11-19 17:03:37.209813

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b6263a817e79"
down_revision: Union[str, Sequence[str], None] = "d381fa36b217"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(op.f("ix_authors_name"), "authors", ["name"], unique=False)
    op.create_index(op.f("ix_books_isbn"), "books", ["isbn"], unique=True)
    op.create_index(op.f("ix_books_title"), "books", ["title"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_books_isbn"), table_name="books")
    op.drop_index(op.f("ix_books_title"), table_name="books")
    op.drop_index(op.f("ix_authors_name"), table_name="authors")
    # ### end Alembic commands ###
