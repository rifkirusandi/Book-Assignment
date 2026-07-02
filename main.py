"""FastAPI application entry point with middleware and router registration."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import engine, Base
from routers.books import router as books_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create all database tables on startup."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A production-ready Book CRUD API built with FastAPI and SQLAlchemy.",
    lifespan=lifespan,
)

# ── CORS Middleware ──────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(books_router, prefix="/api/v1")


@app.get("/", tags=["health"])
def root():
    """Health-check endpoint."""
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
