"""
Async HTTP client wrapping the backend REST API.
All methods raise on non-2xx responses to surface errors early.
"""
import logging

import httpx

from config import settings

logger = logging.getLogger(__name__)
BASE = settings.BACKEND_URL


async def create_trader(name: str, contact: str, source: str) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            f"{BASE}/traders/",
            json={"name": name, "contact": contact, "source": source},
        )
        resp.raise_for_status()
        return resp.json()


async def update_status(trader_id: str, status: str) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.put(
            f"{BASE}/traders/{trader_id}/status",
            json={"status": status},
        )
        resp.raise_for_status()
        return resp.json()


async def add_deposit(trader_id: str, amount: float) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            f"{BASE}/traders/{trader_id}/deposit",
            json={"amount": amount},
        )
        resp.raise_for_status()
        return resp.json()


async def get_stats() -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{BASE}/stats/overview")
        resp.raise_for_status()
        return resp.json()
