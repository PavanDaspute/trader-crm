"""
Pydantic models and enums for the Trader domain.
Covers request/response shapes and the DB document model.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field


class TraderStatus(str, Enum):
    new = "new"
    registered = "registered"
    funded = "funded"
    active = "active"


class TraderSource(str, Enum):
    telegram = "Telegram"
    ads = "Ads"
    referral = "Referral"
    organic = "Organic"
    other = "Other"


# ─── Request Schemas ────────────────────────────────────────────────────────────

class TraderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    contact: str = Field(..., min_length=1, max_length=200, description="Email, phone, or Telegram handle")
    source: TraderSource = TraderSource.other

    class Config:
        use_enum_values = True


class StatusUpdateRequest(BaseModel):
    status: TraderStatus

    class Config:
        use_enum_values = True


class DepositRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Deposit amount in USD")


# ─── Response Schemas ────────────────────────────────────────────────────────────

class TraderResponse(BaseModel):
    id: str
    name: str
    contact: str
    source: str
    status: str
    initial_deposit: float
    total_deposit: float
    last_activity_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


def trader_from_db(doc: dict) -> TraderResponse:
    """Map a raw MongoDB document to a TraderResponse."""
    return TraderResponse(
        id=str(doc["_id"]),
        name=doc["name"],
        contact=doc["contact"],
        source=doc["source"],
        status=doc["status"],
        initial_deposit=doc.get("initial_deposit", 0.0),
        total_deposit=doc.get("total_deposit", 0.0),
        last_activity_at=doc.get("last_activity_at"),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )
