"""
/stats handler — fetches and displays platform KPIs inline.
"""
import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from api import client as api

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    await message.answer("⏳ Fetching platform stats...")
    try:
        stats = await api.get_stats()
        text = (
            "📊 <b>Trading Platform KPIs</b>\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"👥 Total Traders:     <b>{stats['total_traders']}</b>\n"
            f"📝 Registered:        <b>{stats['registered_traders']}</b>\n"
            f"💰 Funded:            <b>{stats['funded_traders']}</b>\n"
            f"🚀 Active:            <b>{stats['active_traders']}</b>\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"📈 Conversion Rate:   <b>{stats['conversion_rate']}%</b>\n"
            f"⚡ Activation Rate:  <b>{stats['activation_rate']}%</b>\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"💵 Total Deposits:    <b>${stats['total_deposits']:,.2f}</b>\n"
            f"💳 Avg Deposit:       <b>${stats['avg_deposit_per_trader']:,.2f}</b>"
        )
        await message.answer(text, parse_mode="HTML")
    except Exception as e:
        logger.error("Stats fetch failed: %s", e)
        await message.answer("❌ Could not fetch stats. Is the backend running?")
