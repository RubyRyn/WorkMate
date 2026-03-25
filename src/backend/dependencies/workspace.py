from sqlalchemy.orm import Session, joinedload

from src.backend.models.notion import NotionConnection


def get_workspace_filter(user_id: int, db: Session) -> dict | None:
    """Build a ChromaDB where filter for the user's connected workspaces."""
    connections = (
        db.query(NotionConnection)
        .options(joinedload(NotionConnection.workspace))
        .filter(NotionConnection.user_id == user_id)
        .all()
    )
    workspace_ids = [conn.workspace.workspace_id for conn in connections]
    if not workspace_ids:
        return None  # No filter — allow legacy data access
    return {"workspace_id": {"$in": workspace_ids}}