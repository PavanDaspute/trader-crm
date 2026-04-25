"""
Analytics routes — all KPI and funnel endpoints.
"""
from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_db
from app.services import stats_service

router = APIRouter(prefix="/stats", tags=["Analytics"])


def db_dep() -> AsyncIOMotorDatabase:
    return get_db()


@router.get("/overview")
async def overview(db: AsyncIOMotorDatabase = Depends(db_dep)):
    """High-level KPI summary: totals, conversion rate, deposits."""
    return await stats_service.get_overview(db)


@router.get("/funnel")
async def funnel(db: AsyncIOMotorDatabase = Depends(db_dep)):
    """Trader counts at each lifecycle stage (new → active)."""
    return await stats_service.get_funnel(db)


@router.get("/timeseries")
async def timeseries(
    days: int = Query(30, ge=1, le=365, description="Number of past days to include"),
    db: AsyncIOMotorDatabase = Depends(db_dep),
):
    """Day-bucketed traders and deposits over the last N days."""
    return await stats_service.get_timeseries(db, days=days)


@router.get("/sources")
async def source_breakdown(db: AsyncIOMotorDatabase = Depends(db_dep)):
    """Per-source trader counts, deposits, and conversion rates."""
    return await stats_service.get_source_breakdown(db)
