from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.backend.config import settings
from src.backend.database import Base, engine
from src.backend.routers import admin, auth, conversations, notion, upload


def create_app() -> FastAPI:
    Base.metadata.create_all(bind=engine)

    app = FastAPI(title="WorkMate API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_URL],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Health check ─────────────────────────────────────────────
    # Lightweight endpoint used by EKS liveness and readiness probes.
    # Intentionally placed before router includes so it is always
    # reachable even if downstream routers fail to load.
    @app.get("/health", tags=["health"], include_in_schema=False)
    async def health_check() -> JSONResponse:
        return JSONResponse({"status": "ok"})

    app.include_router(auth.router)
    app.include_router(admin.router)
    app.include_router(conversations.router)
    app.include_router(upload.router)
    app.include_router(notion.router)

    return app
