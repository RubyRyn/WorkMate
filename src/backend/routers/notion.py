import logging
from datetime import datetime, timezone
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session, joinedload

from src.backend.config import settings
from src.backend.database import SessionLocal, get_db
from src.backend.dependencies.auth import get_current_user, verify_token
from src.backend.dependencies.services import get_chroma_manager
from src.backend.load.chroma_manager import ChromaManager
from src.backend.models.notion import NotionConnection, NotionWorkspace
from src.backend.models.user import User
from src.backend.schemas.notion import NotionAuthURL, NotionWorkspaceResponse
from src.backend.utils.encryption import decrypt_token, encrypt_token

router = APIRouter(prefix="/api/notion", tags=["notion"])
logger = logging.getLogger(__name__)

NOTION_AUTH_URL = "https://api.notion.com/v1/oauth/authorize"
NOTION_TOKEN_URL = "https://api.notion.com/v1/oauth/token"


def _ingest_workspace(workspace_db_id: int, access_token: str, notion_workspace_id: str):
    """Background task: fetch from Notion, chunk, and store in ChromaDB."""
    import os
    import sys

    # Add src/Notion to sys.path so notion_fetcher's internal imports resolve
    notion_dir = os.path.join(os.path.dirname(__file__), "../../Notion")
    notion_dir = os.path.abspath(notion_dir)
    if notion_dir not in sys.path:
        sys.path.insert(0, notion_dir)

    from src.Notion.notion_fetcher.Notion_Fetcher import NotionFetcher
    from src.backend.transform.notion_ingestory import NotionIngestor

    db = SessionLocal()
    try:
        workspace = db.query(NotionWorkspace).get(workspace_db_id)
        if not workspace:
            logger.error(f"Workspace {workspace_db_id} not found for ingestion")
            return

        workspace.sync_status = "syncing"
        db.commit()

        logger.info(f"Starting ingestion for workspace: {workspace.workspace_name}")

        # Fetch documents from Notion using the user's access token
        fetcher = NotionFetcher(access_token)
        documents = fetcher.fetch_all()

        # Convert NotionDocument objects to dicts for the ingestor
        raw_docs = [doc.to_dict() for doc in documents]

        # Run the ingestion pipeline with workspace_id tagging
        ingestor = NotionIngestor(workspace_id=notion_workspace_id)
        ingestor.run_pipeline_from_docs(raw_docs)

        workspace.sync_status = "idle"
        workspace.last_synced_at = datetime.now(timezone.utc)
        db.commit()

        logger.info(
            f"Ingestion complete for workspace: {workspace.workspace_name} "
            f"({len(raw_docs)} documents)"
        )
    except Exception as e:
        logger.error(f"Ingestion failed for workspace {workspace_db_id}: {e}")
        try:
            workspace = db.query(NotionWorkspace).get(workspace_db_id)
            if workspace:
                workspace.sync_status = "error"
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


@router.get("/connect", response_model=NotionAuthURL)
def notion_connect(current_user: User = Depends(get_current_user)):
    """Return the Notion OAuth authorization URL.
    Embeds the user's JWT in the state parameter so we can identify them in the callback.
    """
    from src.backend.dependencies.auth import create_access_token

    jwt_token = create_access_token({"sub": str(current_user.id)})

    params = {
        "client_id": settings.NOTION_OAUTH_CLIENT_ID,
        "redirect_uri": settings.NOTION_REDIRECT_URI,
        "response_type": "code",
        "owner": "user",
        "state": jwt_token,
    }
    authorization_url = f"{NOTION_AUTH_URL}?{urlencode(params)}"
    return NotionAuthURL(authorization_url=authorization_url)


@router.get("/callback")
async def notion_callback(
    code: str,
    state: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Handle the Notion OAuth callback.
    Exchanges the code for an access token, stores workspace + connection,
    and triggers background ingestion if the workspace is new.
    """
    # Verify the JWT from the state parameter to identify the user
    payload = verify_token(state)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired state token",
        )
    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Exchange the authorization code for an access token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            NOTION_TOKEN_URL,
            json={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.NOTION_REDIRECT_URI,
            },
            auth=(settings.NOTION_OAUTH_CLIENT_ID, settings.NOTION_OAUTH_CLIENT_SECRET),
        )

    if token_response.status_code != 200:
        logger.error(f"Notion token exchange failed: {token_response.text}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange code for Notion access token",
        )

    token_data = token_response.json()
    access_token = token_data.get("access_token")
    bot_id = token_data.get("bot_id", "")
    workspace_info = token_data.get("workspace", {})
    notion_workspace_id = token_data.get("workspace_id", "")
    workspace_name = token_data.get("workspace_name", workspace_info.get("name", "Untitled Workspace"))
    workspace_icon = token_data.get("workspace_icon", workspace_info.get("icon", None))

    # Check if this workspace already exists in our DB
    workspace = (
        db.query(NotionWorkspace)
        .filter(NotionWorkspace.workspace_id == notion_workspace_id)
        .first()
    )
    is_new_workspace = workspace is None

    if is_new_workspace:
        workspace = NotionWorkspace(
            workspace_id=notion_workspace_id,
            workspace_name=workspace_name,
            workspace_icon=workspace_icon,
            bot_id=bot_id,
            sync_status="idle",
        )
        db.add(workspace)
        db.commit()
        db.refresh(workspace)

    # Check if the user already has a connection to this workspace
    existing_connection = (
        db.query(NotionConnection)
        .filter(
            NotionConnection.user_id == user_id,
            NotionConnection.workspace_id == workspace.id,
        )
        .first()
    )

    if existing_connection:
        # Update the access token (user re-authorized)
        existing_connection.access_token = encrypt_token(access_token)
        db.commit()
    else:
        connection = NotionConnection(
            user_id=user_id,
            workspace_id=workspace.id,
            access_token=encrypt_token(access_token),
        )
        db.add(connection)
        db.commit()

    # Trigger background ingestion if this is a new workspace
    if is_new_workspace:
        background_tasks.add_task(
            _ingest_workspace, workspace.id, access_token, notion_workspace_id
        )

    redirect_url = f"{settings.FRONTEND_URL}/settings?notion=connected"
    return RedirectResponse(url=redirect_url)


@router.get("/workspaces", response_model=list[NotionWorkspaceResponse])
def list_workspaces(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all Notion workspaces connected by the current user."""
    connections = (
        db.query(NotionConnection)
        .options(joinedload(NotionConnection.workspace))
        .filter(NotionConnection.user_id == current_user.id)
        .all()
    )
    results = []
    for conn in connections:
        ws = conn.workspace
        results.append(
            NotionWorkspaceResponse(
                id=ws.id,
                workspace_id=ws.workspace_id,
                workspace_name=ws.workspace_name,
                workspace_icon=ws.workspace_icon,
                sync_status=ws.sync_status,
                last_synced_at=ws.last_synced_at,
                connected_at=conn.connected_at,
            )
        )
    return results


@router.post("/workspaces/{workspace_id}/sync")
def sync_workspace(
    workspace_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    chroma: ChromaManager = Depends(get_chroma_manager),
):
    """Trigger a manual re-sync for a connected workspace."""
    connection = (
        db.query(NotionConnection)
        .filter(
            NotionConnection.user_id == current_user.id,
            NotionConnection.workspace_id == workspace_id,
        )
        .first()
    )
    if not connection:
        raise HTTPException(status_code=404, detail="Workspace connection not found")

    workspace = connection.workspace
    if workspace.sync_status == "syncing":
        return {"status": "already_syncing"}

    # Delete existing chunks for this workspace before re-ingesting
    chroma.delete_by_workspace(workspace.workspace_id)

    workspace.sync_status = "syncing"
    db.commit()

    access_token = decrypt_token(connection.access_token)
    background_tasks.add_task(
        _ingest_workspace, workspace.id, access_token, workspace.workspace_id
    )

    return {"status": "syncing"}


@router.delete("/workspaces/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def disconnect_workspace(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    chroma: ChromaManager = Depends(get_chroma_manager),
):
    """Disconnect the current user from a Notion workspace.
    If this is the last connected user, also delete workspace data from ChromaDB.
    """
    connection = (
        db.query(NotionConnection)
        .filter(
            NotionConnection.user_id == current_user.id,
            NotionConnection.workspace_id == workspace_id,
        )
        .first()
    )
    if not connection:
        raise HTTPException(status_code=404, detail="Workspace connection not found")

    workspace = connection.workspace
    db.delete(connection)
    db.commit()

    # Check if any other users are still connected to this workspace
    remaining = (
        db.query(NotionConnection)
        .filter(NotionConnection.workspace_id == workspace_id)
        .count()
    )

    if remaining == 0:
        # Last user disconnected — purge workspace data
        chroma.delete_by_workspace(workspace.workspace_id)
        db.delete(workspace)
        db.commit()
