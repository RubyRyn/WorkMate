import logging
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from src.backend.dependencies.auth import get_current_user
from src.backend.dependencies.services import get_chroma_manager
from src.backend.load.chroma_manager import ChromaManager
from src.backend.models.user import User
from src.backend.schemas.upload import UploadResponse
from src.backend.transform.file_ingestor import (
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE,
    FileIngestor,
)

router = APIRouter(prefix="/api/upload", tags=["upload"])
logger = logging.getLogger(__name__)

_file_ingestor = FileIngestor()


def _get_extension(filename: str) -> str:
    return "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


@router.post("/", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    chroma: ChromaManager = Depends(get_chroma_manager),
):
    # Validate extension
    ext = _get_extension(file.filename or "")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Read and validate size
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024 * 1024)} MB.",
        )

    if not file_bytes:
        raise HTTPException(status_code=400, detail="File is empty.")

    try:
        result = _file_ingestor.ingest(
            file_bytes=file_bytes,
            filename=file.filename or "unknown",
            user_id=current_user.id,
            chroma=chroma,
        )
    except Exception as e:
        logger.error(f"File ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process file: {e}")

    return UploadResponse(
        filename=result["filename"],
        chunk_count=result["chunk_count"],
        status="success",
        message=f"File '{result['filename']}' uploaded and indexed ({result['chunk_count']} chunks).",
    )


@router.post("/batch", response_model=List[UploadResponse])
async def upload_batch(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    chroma: ChromaManager = Depends(get_chroma_manager),
):
    responses: List[UploadResponse] = []

    for file in files:
        # Validate extension
        ext = _get_extension(file.filename or "")
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '{ext}' for file '{file.filename}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
            )

        # Read and validate size
        file_bytes = await file.read()
        if len(file_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File '{file.filename}' too large. Maximum size is {MAX_FILE_SIZE // (1024 * 1024)} MB.",
            )

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"File '{file.filename}' is empty.",
            )

        try:
            result = _file_ingestor.ingest(
                file_bytes=file_bytes,
                filename=file.filename or "unknown",
                user_id=current_user.id,
                chroma=chroma,
            )
        except Exception as e:
            logger.error(f"File ingestion failed for '{file.filename}': {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process file '{file.filename}': {e}",
            )

        responses.append(
            UploadResponse(
                filename=result["filename"],
                chunk_count=result["chunk_count"],
                status="success",
                message=f"File '{result['filename']}' uploaded and indexed ({result['chunk_count']} chunks).",
            )
        )

    return responses
