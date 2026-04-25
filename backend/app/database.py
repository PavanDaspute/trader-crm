"""
Async MongoDB connection management via Motor.
Exposes a single database instance reused across the app.
"""
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

logger = logging.getLogger(__name__)

client: AsyncIOMotorClient = None


async def connect_db():
    """Initialize Motor client on app startup."""
    global client
    client = AsyncIOMotorClient(settings.MONGO_URL)
    logger.info("Connected to MongoDB at %s", settings.MONGO_URL)


async def close_db():
    """Close Motor client on app shutdown."""
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed")


def get_db():
    """Return the target database handle."""
    return client[settings.MONGO_DB]
