from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import auth
from app.db.session import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Prototype-grade: create tables that don't exist yet, no migrations.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Pre-legal API", version="0.1.0", lifespan=lifespan)

app.include_router(auth.router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
