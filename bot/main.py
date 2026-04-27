"""
Telegram Bot entry point.
Registers all handlers and starts polling.
"""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings
from handlers import start, add_trader, update_status, deposit, stats

logging.basicConfig(
    stream=sys.stdout,
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Register routers — order matters for callback priority:
    # start must come first (handles nav:* callbacks shared across flows)
    dp.include_router(start.router)
    dp.include_router(add_trader.router)    # includes nav:add_trader + AddTrader FSM
    dp.include_router(update_status.router) # includes nav:update_status + UpdateStatus FSM + set_status callbacks
    dp.include_router(deposit.router)       # includes nav:deposit + Deposit FSM
    dp.include_router(stats.router)         # includes nav:stats

    logger.info("Starting TraderCRM Bot (backend: %s)", settings.BACKEND_URL)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
