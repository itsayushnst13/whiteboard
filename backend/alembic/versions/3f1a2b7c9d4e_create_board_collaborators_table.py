"""create board_collaborators table

Revision ID: 3f1a2b7c9d4e
Revises: 9982c54f545a
Create Date: 2026-08-02 00:00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3f1a2b7c9d4e"
down_revision: str | None = "9982c54f545a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "board_collaborators",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("board_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="editor"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["board_id"], ["boards.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("board_id", "user_id", name="uq_board_collaborators_board_id_user_id"),
    )
    op.create_index("ix_board_collaborators_board_id", "board_collaborators", ["board_id"])
    op.create_index("ix_board_collaborators_user_id", "board_collaborators", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_board_collaborators_user_id", table_name="board_collaborators")
    op.drop_index("ix_board_collaborators_board_id", table_name="board_collaborators")
    op.drop_table("board_collaborators")
