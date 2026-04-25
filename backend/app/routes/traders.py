"""
Trader CRUD routes.
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_db
from app.models.trader import DepositRequest, StatusUpdateRequest, TraderCreate, TraderResponse
from app.services import trader_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/traders", tags=["Traders"])


def db_dep() -> AsyncIOMotorDatabase:
    return get_db()


@router.post("/", response_model=TraderResponse, status_code=201)
async def create_trader(payload: TraderCreate, db: AsyncIOMotorDatabase = Depends(db_dep)):
    """Create a new trader lead."""
    return await trader_service.create_trader(db, payload)


@router.get("/", response_model=list[TraderResponse])
async def list_traders(
    status: Optional[str] = Query(None, description="Filter by status"),
    source: Optional[str] = Query(None, description="Filter by source"),
    db: AsyncIOMotorDatabase = Depends(db_dep),
):
    """List all traders with optional filters."""
    return await trader_service.list_traders(db, status_filter=status, source_filter=source)


@router.put("/{trader_id}/status", response_model=TraderResponse)
async def update_status(
    trader_id: str,
    payload: StatusUpdateRequest,
    db: AsyncIOMotorDatabase = Depends(db_dep),
):
    """Update a trader's lifecycle stage."""
    return await trader_service.update_trader_status(db, trader_id, payload)


@router.post("/{trader_id}/deposit", response_model=TraderResponse)
async def add_deposit(
    trader_id: str,
    payload: DepositRequest,
    db: AsyncIOMotorDatabase = Depends(db_dep),
):
    """Record a deposit for a trader."""
    return await trader_service.add_deposit(db, trader_id, payload)
