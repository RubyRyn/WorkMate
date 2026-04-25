# ─────────────────────────────────────────────────────────────────
# Stage 1: Builder
# Install uv and sync dependencies from the lockfile into a venv.
# ─────────────────────────────────────────────────────────────────
FROM --platform=linux/amd64 python:3.13-slim AS builder

# Install uv (fast Python package manager used by this project)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency manifests first — maximises layer cache reuse
# on subsequent builds where only application code changes.
COPY pyproject.toml uv.lock ./

# Sync locked dependencies into the project venv.
# --frozen  → fail fast if lockfile is stale (enforces reproducibility)
# --no-dev  → exclude dev/test extras from the production image
# --no-cache → skip uv's HTTP cache; keeps the layer lean
RUN uv sync --frozen --no-dev --no-cache

# ─────────────────────────────────────────────────────────────────
# Stage 2: Runtime
# Lean final image — only the pre-built venv and application source.
# ─────────────────────────────────────────────────────────────────
FROM --platform=linux/amd64 python:3.13-slim AS runtime

# Create a non-root user (defence-in-depth for container security)
RUN groupadd --gid 1000 appuser && \
    useradd  --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

WORKDIR /app

# Copy the populated venv from the builder stage
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application source (secrets + DBs are excluded via .dockerignore)
COPY --chown=appuser:appuser main.py ./main.py
COPY --chown=appuser:appuser src/    ./src/

# BM25Manager persists its index to /app/workmate_db/bm25_index.pkl.
# Pre-create the directory with appuser ownership so the non-root runtime
# can write to it. (Chroma itself runs remotely via CHROMA_HOST.)
RUN mkdir -p /app/workmate_db && chown appuser:appuser /app/workmate_db

# Activate the venv by prepending it to PATH
ENV PATH="/app/.venv/bin:$PATH" \
    # Prevent Python from writing .pyc files inside the container
    PYTHONDONTWRITEBYTECODE=1   \
    # Ensure stdout/stderr are flushed immediately (important for logs)
    PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000

# Production: no --reload flag; scale via WEB_CONCURRENCY env var if needed
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
