"""
Trader CRUD service layer.
All DB interactions are async via Motor.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.trader import (
    DepositRequest,
    StatusUpdateRequest,
    TraderCreate,
    TraderResponse,
    trader_from_db,
)

logger = logging.getLogger(__name__)
COLLECTION = "traders"


async def create_trader(db: AsyncIOMotorDatabase, payload: TraderCreate) -> TraderResponse:
    now = datetime.now(timezone.utc)
    doc = {
        "name": payload.name,
        "contact": payload.contact,
        "source": payload.source,
        "status": "new",
        "initial_deposit": 0.0,
        "total_deposit": 0.0,
        "last_activity_at": None,
        "created_at": now,
        "updated_at": now,
    }
    result = await db[COLLECTION].insert_one(doc)
    doc["_id"] = result.inserted_id
    logger.info("Created trader %s (%s)", doc["name"], result.inserted_id)
    return trader_from_db(doc)


async def list_traders(
    db: AsyncIOMotorDatabase,
    status_filter: Optional[str] = None,
    source_filter: Optional[str] = None,
) -> list[TraderResponse]:
    query: dict = {}
    if status_filter:
        query["status"] = status_filter
    if source_filter:
        query["source"] = source_filter

    cursor = db[COLLECTION].find(query).sort("created_at", -1)
    docs = await cursor.to_list(length=1000)
    return [trader_from_db(d) for d in docs]


async def get_trader_by_id(db: AsyncIOMotorDatabase, trader_id: str) -> dict:
    if not ObjectId.is_valid(trader_id):
        raise HTTPException(status_code=400, detail="Invalid trader ID format")
    doc = await db[COLLECTION].find_one({"_id": ObjectId(trader_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Trader not found")
    return doc


async def update_trader_status(
    db: AsyncIOMotorDatabase, trader_id: str, payload: StatusUpdateRequest
) -> TraderResponse:
    doc = await get_trader_by_id(db, trader_id)
    now = datetime.now(timezone.utc)
    await db[COLLECTION].update_one(
        {"_id": ObjectId(trader_id)},
        {"$set": {"status": payload.status, "updated_at": now, "last_activity_at": now}},
    )
    doc["status"] = payload.status
    doc["updated_at"] = now
    doc["last_activity_at"] = now
    logger.info("Updated trader %s status → %s", trader_id, payload.status)
    return trader_from_db(doc)


async def add_deposit(
    db: AsyncIOMotorDatabase, trader_id: str, payload: DepositRequest
) -> TraderResponse:
    doc = await get_trader_by_id(db, trader_id)
    now = datetime.now(timezone.utc)
    new_total = doc.get("total_deposit", 0.0) + payload.amount
    update_fields: dict = {
        "total_deposit": new_total,
        "updated_at": now,
        "last_activity_at": now,
    }
    # Record first deposit
    if doc.get("initial_deposit", 0.0) == 0.0:
        update_fields["initial_deposit"] = payload.amount

    await db[COLLECTION].update_one(
        {"_id": ObjectId(trader_id)},
        {"$set": update_fields},
    )
    doc.update(update_fields)
    logger.info("Added deposit $%.2f to trader %s (new total: $%.2f)", payload.amount, trader_id, new_total)
    return trader_from_db(doc)
