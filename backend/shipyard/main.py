"""FastAPI entrypoint.

    uvicorn shipyard.main:app --reload      (dev)
    python -m shipyard.main                  (uses API_HOST / API_PORT)
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .api import router
from .config import settings
from .corpus import corpus
from .state import init_db

_FRONTEND_DIST = settings._resolve("../frontend/dist")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    corpus.load()
    print(f"loaded {len(corpus)} items, {len(corpus.cluster_names)} clusters, "
          f"llm={corpus.facets.get('llm_enabled', False)}")
    yield


app = FastAPI(title="Backlog", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list or ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


# ---- serve the built frontend if present (single-service deploy) ----
if _FRONTEND_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=_FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def spa(full_path: str):
        candidate = _FRONTEND_DIST / full_path
        if candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(_FRONTEND_DIST / "index.html")


def run() -> None:
    import uvicorn

    uvicorn.run(
        "shipyard.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.shipyard_env == "local",
    )


if __name__ == "__main__":
    run()
