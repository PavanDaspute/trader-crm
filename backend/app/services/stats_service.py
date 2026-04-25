"""
Analytics/Stats service — uses MongoDB aggregation pipelines for KPIs.
All methods return pure Python dicts suitable for JSON serialisation.
"""
import logging
from datetime import datetime, timedelta, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)
COLLECTION = "traders"


async def get_overview(db: AsyncIOMotorDatabase) -> dict:
    """Return high-level KPI metrics via aggregation."""
    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_traders": {"$sum": 1},
                "registered_traders": {"$sum": {"$cond": [{"$eq": ["$status", "registered"]}, 1, 0]}},
                "funded_traders": {"$sum": {"$cond": [{"$eq": ["$status", "funded"]}, 1, 0]}},
                "active_traders": {"$sum": {"$cond": [{"$eq": ["$status", "active"]}, 1, 0]}},
                "total_deposits": {"$sum": "$total_deposit"},
            }
        }
    ]
    result = await db[COLLECTION].aggregate(pipeline).to_list(length=1)

    if not result:
        return {
            "total_traders": 0,
            "registered_traders": 0,
            "funded_traders": 0,
            "active_traders": 0,
            "conversion_rate": 0.0,
            "activation_rate": 0.0,
            "total_deposits": 0.0,
            "avg_deposit_per_trader": 0.0,
        }

    row = result[0]
    total = row["total_traders"] or 0
    funded = row["funded_traders"] or 0
    active = row["active_traders"] or 0
    total_deposits = row["total_deposits"] or 0.0

    conversion_rate = round((funded / total * 100), 2) if total > 0 else 0.0
    activation_rate = round((active / funded * 100), 2) if funded > 0 else 0.0
    avg_deposit = round(total_deposits / total, 2) if total > 0 else 0.0

    return {
        "total_traders": total,
        "registered_traders": row["registered_traders"] or 0,
        "funded_traders": funded,
        "active_traders": active,
        "conversion_rate": conversion_rate,
        "activation_rate": activation_rate,
        "total_deposits": round(total_deposits, 2),
        "avg_deposit_per_trader": avg_deposit,
    }


async def get_funnel(db: AsyncIOMotorDatabase) -> list[dict]:
    """Return stage counts in funnel order."""
    stages = ["new", "registered", "funded", "active"]
    pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    result = await db[COLLECTION].aggregate(pipeline).to_list(length=100)
    counts = {row["_id"]: row["count"] for row in result}
    return [{"stage": s, "count": counts.get(s, 0)} for s in stages]


async def get_timeseries(db: AsyncIOMotorDatabase, days: int = 30) -> dict:
    """Return day-bucketed traders created and deposits over the last N days."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    # Traders over time
    traders_pipeline = [
        {"$match": {"created_at": {"$gte": since}}},
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$created_at"},
                    "month": {"$month": "$created_at"},
                    "day": {"$dayOfMonth": "$created_at"},
                },
                "count": {"$sum": 1},
                "deposits": {"$sum": "$total_deposit"},
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1}},
    ]

    raw = await db[COLLECTION].aggregate(traders_pipeline).to_list(length=365)
    series = []
    for row in raw:
        d = row["_id"]
        series.append(
            {
                "date": f"{d['year']}-{d['month']:02d}-{d['day']:02d}",
                "traders": row["count"],
                "deposits": round(row["deposits"], 2),
            }
        )
    return {"series": series, "days": days}


async def get_source_breakdown(db: AsyncIOMotorDatabase) -> list[dict]:
    """Return trader counts and total deposits grouped by acquisition source."""
    pipeline = [
        {
            "$group": {
                "_id": "$source",
                "count": {"$sum": 1},
                "total_deposits": {"$sum": "$total_deposit"},
                "funded": {"$sum": {"$cond": [{"$in": ["$status", ["funded", "active"]]}, 1, 0]}},
            }
        },
        {"$sort": {"count": -1}},
    ]
    result = await db[COLLECTION].aggregate(pipeline).to_list(length=100)
    return [
        {
            "source": row["_id"],
            "count": row["count"],
            "funded": row["funded"],
            "total_deposits": round(row["total_deposits"], 2),
            "conversion_rate": round(row["funded"] / row["count"] * 100, 2) if row["count"] > 0 else 0.0,
        }
        for row in result
    ]
