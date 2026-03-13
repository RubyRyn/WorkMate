from pydantic import BaseModel


class UploadResponse(BaseModel):
    filename: str
    chunk_count: int
    status: str
    message: str
