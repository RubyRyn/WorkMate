from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.backend.database import Base


class NotionWorkspace(Base):
    __tablename__ = "notion_workspaces"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workspace_id: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    workspace_name: Mapped[str] = mapped_column(String, nullable=False)
    workspace_icon: Mapped[str | None] = mapped_column(String, nullable=True)
    bot_id: Mapped[str] = mapped_column(String, nullable=False)
    sync_status: Mapped[str] = mapped_column(String, default="idle", nullable=False)
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    connections: Mapped[list["NotionConnection"]] = relationship(
        "NotionConnection", back_populates="workspace", cascade="all, delete-orphan"
    )


class NotionConnection(Base):
    __tablename__ = "notion_connections"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    workspace_id: Mapped[int] = mapped_column(
        ForeignKey("notion_workspaces.id"), nullable=False, index=True
    )
    access_token: Mapped[str] = mapped_column(String, nullable=False)
    token_type: Mapped[str] = mapped_column(String, default="bearer", nullable=False)
    connected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="notion_connections")  # noqa: F821
    workspace: Mapped["NotionWorkspace"] = relationship(
        "NotionWorkspace", back_populates="connections"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "workspace_id", name="uq_user_workspace"),
    )
