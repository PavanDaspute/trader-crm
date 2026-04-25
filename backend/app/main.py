"""
FastAPI application entry point.
Wires together routes, DB lifecycle, middleware, and logging.
"""
import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import connect_db, close_db
from app.routes import traders, stats

# ─── Logging Setup ──────────────────────────────────────────────────────────────
logging.basicConfig(
    stream=sys.stdout,
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ─── App Init ───────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Trading CRM API",
    description="Trader lifecycle management and conversion analytics for brokerage platforms.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Lifecycle Events ────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    await connect_db()
    logger.info("Trading CRM API started in %s mode", settings.APP_ENV)


@app.on_event("shutdown")
async def shutdown():
    await close_db()

# ─── Routes ─────────────────────────────────────────────────────────────────────
app.include_router(traders.router)
app.include_router(stats.router)


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "trading-crm-api"}
