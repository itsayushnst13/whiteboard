from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BoardCollaborator(Base):
    """Grants a user access to a board they don't own. `role` is either
    ``"editor"`` (draw/edit/erase/undo/redo/export) or ``"viewer"``
    (read-only). The board owner is never a row in this table — ownership
    lives on `Board.owner_id` and always implies full access."""

    __tablename__ = "board_collaborators"
    __table_args__ = (
        UniqueConstraint("board_id", "user_id", name="uq_board_collaborators_board_id_user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    board_id: Mapped[int] = mapped_column(
        ForeignKey("boards.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="editor")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
