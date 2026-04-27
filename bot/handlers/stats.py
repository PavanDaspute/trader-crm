"""
/stats handler — fetches and displays platform KPIs with enhanced formatting.
Also handles the nav:stats callback from the main menu.
"""
import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from api import client as api
from keyboards.main_menu import main_menu_keyboard, MENU_TEXT

logger = logging.getLogger(__name__)
router = Router()

DIVIDER = "━━━━━━━━━━━━━━━━━━━━━━"


def _format_stats(stats: dict) -> str:
    total     = stats.get("total_traders", 0)
    reg       = stats.get("registered_traders", 0)
    funded    = stats.get("funded_traders", 0)
    active    = stats.get("active_traders", 0)
    conv      = stats.get("conversion_rate", 0.0)
    activ     = stats.get("activation_rate", 0.0)
    deposits  = stats.get("total_deposits", 0.0)
    avg_dep   = stats.get("avg_deposit_per_trader", 0.0)

    # Trend bars (simple ASCII representation)
    def bar(val, max_val=100, width=8):
        if max_val == 0:
            return "░" * width
        filled = round((val / max_val) * width)
        return "█" * filled + "░" * (width - filled)

    conv_bar   = bar(conv)
    activ_bar  = bar(activ)

    return (
        f"📊 <b>Platform Stats</b>\n"
        f"{DIVIDER}\n"
        f"👥 Total Traders:    <b>{total:,}</b>\n"
        f"📝 Registered:       <b>{reg:,}</b>\n"
        f"💰 Funded:           <b>{funded:,}</b>\n"
        f"🔥 Active:           <b>{active:,}</b>\n"
        f"{DIVIDER}\n"
        f"📈 Conversion Rate:  <b>{conv:.1f}%</b>  {conv_bar}\n"
        f"⚡ Activation Rate: <b>{activ:.1f}%</b>  {activ_bar}\n"
        f"{DIVIDER}\n"
        f"💵 Total Deposits:   <b>${deposits:,.2f}</b>\n"
        f"📊 Avg Deposit:      <b>${avg_dep:,.2f}</b>"
    )


async def _send_stats(target, edit: bool = False):
    """Fetch stats and send (or edit) formatted output."""
    try:
        stats = await api.get_stats()
        text = _format_stats(stats) + f"\n\n{MENU_TEXT}"
        if edit and hasattr(target, "message"):
            await target.message.edit_text(text, parse_mode="HTML",
                                           reply_markup=main_menu_keyboard())
        elif hasattr(target, "message"):
            # callback but not editing (e.g. after a message)
            await target.message.answer(text, parse_mode="HTML",
                                        reply_markup=main_menu_keyboard())
        else:
            await target.answer(text, parse_mode="HTML",
                                reply_markup=main_menu_keyboard())
    except Exception as e:
        logger.error("Stats fetch failed: %s", e)
        err = "❌ Could not fetch stats. Is the backend reachable?"
        if hasattr(target, "message"):
            await target.message.answer(err)
        else:
            await target.answer(err)


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    await _send_stats(message)


@router.callback_query(F.data == "nav:stats")
async def nav_stats(callback: CallbackQuery):
    await _send_stats(callback, edit=True)
