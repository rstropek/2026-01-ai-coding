"""Add person table and assignment to todos.

Revision ID: 89fa68024953
Revises: b38fb0519c83
Create Date: 2026-01-28 11:35:31.266321

"""

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "89fa68024953"
down_revision: str | Sequence[str] | None = "b38fb0519c83"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create people table
    op.create_table("people",
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("name", sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_people_id"), "people", ["id"], unique=False)

    # Add assigned_to_id column to todo_items using batch mode for SQLite
    with op.batch_alter_table("todo_items", schema=None) as batch_op:
        batch_op.add_column(sa.Column("assigned_to_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_todo_items_assigned_to_id_people", "people", ["assigned_to_id"], ["id"])


def downgrade() -> None:
    """Downgrade schema."""
    # Remove assigned_to_id from todo_items using batch mode for SQLite
    with op.batch_alter_table("todo_items", schema=None) as batch_op:
        batch_op.drop_constraint("fk_todo_items_assigned_to_id_people", type_="foreignkey")
        batch_op.drop_column("assigned_to_id")

    # Drop people table
    op.drop_index(op.f("ix_people_id"), table_name="people")
    op.drop_table("people")
