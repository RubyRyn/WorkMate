from datetime import datetime

from pydantic import BaseModel


class NotionAuthURL(BaseModel):
    authorization_url: str


class NotionWorkspaceResponse(BaseModel):
    id: int
    workspace_id: str
    workspace_name: str
    workspace_icon: str | None
    sync_status: str
    last_synced_at: datetime | None
    connected_at: datetime

    model_config = {"from_attributes": True}
