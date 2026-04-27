"""
/update_status handler — upgraded with inline trader picker and lifecycle suggestions.

Flow:
  /update_status (or nav button)
      → Show trader list (inline keyboard)
      → User selects trader OR falls back to manual ID
      → Show status options (suggested next stage highlighted)
      → Confirm update → show smart nav
"""
import logging

import httpx
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery, Message
)

from api import client as api
from keyboards.main_menu import main_menu_keyboard, MENU_TEXT
from keyboards.trader_select import trader_select_keyboard, no_traders_keyboard
from keyboards.status_select import status_select_keyboard, suggested_next
from states.trader_states import UpdateStatusStates

logger = logging.getLogger(__name__)
router = Router()

LIFECYCLE_ORDER = ["new", "registered", "funded", "active"]


# ─── Entry points ──────────────────────────────────────────────────────────────

async def _show_trader_list(target, state: FSMContext, action: str = "update_status"):
    """Shared helper to fetch and display the trader picker."""
    await state.set_state(UpdateStatusStates.selecting_trader)
    try:
        traders = await api.list_traders(limit=8)
    except Exception as e:
        logger.error("Failed to fetch traders: %s", e)
        traders = []

    if not traders:
        if hasattr(target, "message"):
            msg = target.message
        else:
            msg = target
        await msg.answer(
            "⚠️ No traders found. Add one first!",
            reply_markup=no_traders_keyboard(),
        )
        await state.clear()
        return

    text = (
        "🔄 <b>Update Trader Status</b>\n\n"
        "Select a trader to update:"
    )
    if hasattr(target, "message"):
        await target.message.edit_text(text, parse_mode="HTML",
                                       reply_markup=trader_select_keyboard(traders, action))
    else:
        await target.answer(text, parse_mode="HTML",
                            reply_markup=trader_select_keyboard(traders, action))


@router.message(Command("update_status"))
async def cmd_update_status(message: Message, state: FSMContext):
    await _show_trader_list(message, state)


@router.callback_query(F.data == "nav:update_status")
async def nav_update_status(callback: CallbackQuery, state: FSMContext):
    await _show_trader_list(callback, state)


# ─── Trader selection callback ──────────────────────────────────────────────────

@router.callback_query(
    UpdateStatusStates.selecting_trader,
    F.data.startswith("select_trader:update_status:"),
)
async def on_trader_selected(callback: CallbackQuery, state: FSMContext):
    trader_id = callback.data.split(":")[-1]

    if trader_id == "MANUAL":
        # Fallback: ask for manual ID entry
        await state.set_state(UpdateStatusStates.manual_trader_id)
        await callback.message.edit_text(
            "✏️ Enter the trader's <b>24-character ID</b>:",
            parse_mode="HTML",
        )
        return

    # Store trader and fetch their current status to suggest next step
    try:
        traders = await api.list_traders(limit=50)
        trader = next((t for t in traders if t["id"] == trader_id), None)
    except Exception:
        trader = None

    current_status = trader["status"] if trader else "new"
    trader_name = trader["name"] if trader else "Trader"
    next_stage = suggested_next(current_status)

    await state.update_data(
        trader_id=trader_id,
        trader_name=trader_name,
        current_status=current_status,
    )
    await state.set_state(UpdateStatusStates.selecting_status)

    hint = f"\n💡 Suggested next stage: <b>{next_stage.upper()}</b>" if next_stage else ""
    await callback.message.edit_text(
        f"👤 <b>{trader_name}</b> — currently <b>{current_status.upper()}</b>{hint}\n\n"
        f"Select the new lifecycle stage:",
        parse_mode="HTML",
        reply_markup=status_select_keyboard(current_status),
    )


@router.message(UpdateStatusStates.manual_trader_id)
async def process_manual_id(message: Message, state: FSMContext):
    trader_id = message.text.strip()
    if len(trader_id) != 24:
        await message.answer("⚠️ That doesn't look like a valid ID (24 characters). Try again:")
        return

    # Try to look up current status for the suggestion
    try:
        traders = await api.list_traders(limit=100)
        trader = next((t for t in traders if t["id"] == trader_id), None)
    except Exception:
        trader = None

    current_status = trader["status"] if trader else "new"
    trader_name = trader["name"] if trader else "Trader"
    next_stage = suggested_next(current_status)

    await state.update_data(
        trader_id=trader_id,
        trader_name=trader_name,
        current_status=current_status,
    )
    await state.set_state(UpdateStatusStates.selecting_status)

    hint = f"\n💡 Suggested next stage: <b>{next_stage.upper()}</b>" if next_stage else ""
    await message.answer(
        f"👤 <b>{trader_name}</b> — currently <b>{current_status.upper()}</b>{hint}\n\n"
        f"Select the new lifecycle stage:",
        parse_mode="HTML",
        reply_markup=status_select_keyboard(current_status),
    )


# ─── Status selection callback ──────────────────────────────────────────────────

@router.callback_query(
    UpdateStatusStates.selecting_status,
    F.data.startswith("set_status:"),
)
async def on_status_selected(callback: CallbackQuery, state: FSMContext):
    new_status = callback.data.split(":")[-1]
    data = await state.get_data()
    await state.clear()

    try:
        trader = await api.update_status(data["trader_id"], new_status)
        stage_emoji = {"new": "🆕", "registered": "📝", "funded": "💰", "active": "🚀"}.get(new_status, "✅")
        await callback.message.edit_text(
            f"✅ <b>Status Updated!</b>\n\n"
            f"👤 <b>{trader['name']}</b>\n"
            f"{stage_emoji} New Stage: <b>{trader['status'].upper()}</b>\n"
            f"📞 Contact: {trader['contact']}\n\n"
            f"{MENU_TEXT}",
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(),
        )
    except httpx.HTTPStatusError as e:
        detail = e.response.json().get("detail", "Unknown error")
        await callback.message.edit_text(f"❌ Error: {detail}\n\n{MENU_TEXT}",
                                         parse_mode="HTML", reply_markup=main_menu_keyboard())
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        await callback.message.edit_text(f"❌ Unexpected error occurred.\n\n{MENU_TEXT}",
                                         parse_mode="HTML", reply_markup=main_menu_keyboard())
