"""Add persons table and assigned_to FK on todo_items

Revision ID: 7f893d01c5cf
Revises: b38fb0519c83
Create Date: 2026-02-19 10:45:08.873828

"""

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "7f893d01c5cf"
down_revision: str | Sequence[str] | None = "b38fb0519c83"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "persons",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_persons_id"), "persons", ["id"], unique=False)
    with op.batch_alter_table("todo_items") as batch_op:
        batch_op.add_column(sa.Column("assigned_to_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_todo_items_assigned_to_id", "persons", ["assigned_to_id"], ["id"])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("todo_items") as batch_op:
        batch_op.drop_constraint("fk_todo_items_assigned_to_id", type_="foreignkey")
        batch_op.drop_column("assigned_to_id")
    op.drop_index(op.f("ix_persons_id"), table_name="persons")
    op.drop_table("persons")
