from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse

from app.api import auth, chat, documents
from app.core.config import settings
from app.db.session import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Prototype-grade: create tables that don't exist yet, no migrations.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Pre-legal API", version="0.1.0", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


def _mount_frontend(app: FastAPI) -> None:
    """Serve the Next.js static export, if it has been built.

    Any path that isn't `/api/*` or `/health` and matches a file under
    `frontend_dir` (e.g. `/_next/static/...`) is served directly; everything
    else falls back to `index.html` so client-side routing works.
    """
    frontend_dir = settings.frontend_dir
    index = frontend_dir / "index.html"
    if not index.exists():
        return

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa_fallback(full_path: str):
        if full_path.startswith("api/") or full_path in {"health", "openapi.json"}:
            return JSONResponse({"detail": "Not Found"}, status_code=404)
        candidate = frontend_dir / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(index)


_mount_frontend(app)
