"""
/deposit handler — upgraded with inline trader picker and validated amount entry.

Flow:
  /deposit (or nav button)
      → Show trader list (inline keyboard)
      → User selects trader OR falls back to manual ID
      → Ask for deposit amount (validated numeric)
      → Confirm → Show enriched success card + smart nav
"""
import logging

import httpx
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from api import client as api
from keyboards.main_menu import main_menu_keyboard, MENU_TEXT
from keyboards.trader_select import trader_select_keyboard, no_traders_keyboard
from states.trader_states import DepositStates

logger = logging.getLogger(__name__)
router = Router()


# ─── Entry points ──────────────────────────────────────────────────────────────

async def _show_trader_list(target, state: FSMContext, action: str = "deposit"):
    """Shared helper to fetch and display the trader picker."""
    await state.set_state(DepositStates.selecting_trader)
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

    text = "💰 <b>Record Trader Deposit</b>\n\nSelect a trader:"
    if hasattr(target, "message"):
        await target.message.edit_text(text, parse_mode="HTML",
                                       reply_markup=trader_select_keyboard(traders, action))
    else:
        await target.answer(text, parse_mode="HTML",
                            reply_markup=trader_select_keyboard(traders, action))


@router.message(Command("deposit"))
async def cmd_deposit(message: Message, state: FSMContext):
    await _show_trader_list(message, state)


@router.callback_query(F.data == "nav:deposit")
async def nav_deposit(callback: CallbackQuery, state: FSMContext):
    await _show_trader_list(callback, state)


# ─── Trader selection callback ──────────────────────────────────────────────────

@router.callback_query(
    DepositStates.selecting_trader,
    F.data.startswith("select_trader:deposit:"),
)
async def on_trader_selected(callback: CallbackQuery, state: FSMContext):
    trader_id = callback.data.split(":")[-1]

    if trader_id == "MANUAL":
        await state.set_state(DepositStates.manual_trader_id)
        await callback.message.edit_text(
            "✏️ Enter the trader's <b>24-character ID</b>:",
            parse_mode="HTML",
        )
        return

    # Look up trader name for context
    try:
        traders = await api.list_traders(limit=50)
        trader = next((t for t in traders if t["id"] == trader_id), None)
    except Exception:
        trader = None

    trader_name = trader["name"] if trader else "Trader"
    current_total = trader["total_deposit"] if trader else 0.0

    await state.update_data(
        trader_id=trader_id,
        trader_name=trader_name,
        current_total=current_total,
    )
    await state.set_state(DepositStates.waiting_for_amount)
    await callback.message.edit_text(
        f"👤 <b>{trader_name}</b>\n"
        f"💼 Current Total: <b>${current_total:,.2f}</b>\n\n"
        f"Enter the <b>deposit amount</b> (USD):",
        parse_mode="HTML",
    )


@router.message(DepositStates.manual_trader_id)
async def process_manual_id(message: Message, state: FSMContext):
    trader_id = message.text.strip()
    if len(trader_id) != 24:
        await message.answer("⚠️ Invalid ID format. Please enter the 24-character trader ID:")
        return

    try:
        traders = await api.list_traders(limit=100)
        trader = next((t for t in traders if t["id"] == trader_id), None)
    except Exception:
        trader = None

    trader_name = trader["name"] if trader else "Trader"
    current_total = trader["total_deposit"] if trader else 0.0

    await state.update_data(
        trader_id=trader_id,
        trader_name=trader_name,
        current_total=current_total,
    )
    await state.set_state(DepositStates.waiting_for_amount)
    await message.answer(
        f"👤 <b>{trader_name}</b>\n"
        f"💼 Current Total: <b>${current_total:,.2f}</b>\n\n"
        f"Enter the <b>deposit amount</b> (USD):",
        parse_mode="HTML",
    )


# ─── Amount entry ──────────────────────────────────────────────────────────────

@router.message(DepositStates.waiting_for_amount)
async def process_amount(message: Message, state: FSMContext):
    raw = message.text.strip().replace(",", "").replace("$", "").replace("₹", "")
    try:
        amount = float(raw)
        if amount <= 0:
            raise ValueError("Must be positive")
    except ValueError:
        await message.answer(
            "⚠️ Please enter a valid positive amount.\n"
            "Examples: <code>500</code>  <code>1250.50</code>  <code>10000</code>",
            parse_mode="HTML",
        )
        return

    data = await state.get_data()
    await state.clear()

    try:
        trader = await api.add_deposit(data["trader_id"], amount)
        prev_total = data.get("current_total", 0.0)
        new_total = trader["total_deposit"]
        growth = ((new_total - prev_total) / prev_total * 100) if prev_total > 0 else None

        growth_line = (
            f"📈 Portfolio Growth: <b>+{growth:.1f}%</b>\n" if growth else ""
        )

        await message.answer(
            f"✅ <b>Deposit Recorded!</b>\n\n"
            f"👤 Trader: <b>{trader['name']}</b>\n"
            f"💵 Added: <b>${amount:,.2f}</b>\n"
            f"💼 Total Deposits: <b>${new_total:,.2f}</b>\n"
            f"{growth_line}"
            f"📊 Status: <b>{trader['status'].upper()}</b>\n\n"
            f"{MENU_TEXT}",
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(),
        )
    except httpx.HTTPStatusError as e:
        detail = e.response.json().get("detail", "Unknown error")
        await message.answer(f"❌ Error: {detail}\n\n{MENU_TEXT}",
                             parse_mode="HTML", reply_markup=main_menu_keyboard())
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        await message.answer(f"❌ Unexpected error occurred.\n\n{MENU_TEXT}",
                             parse_mode="HTML", reply_markup=main_menu_keyboard())
