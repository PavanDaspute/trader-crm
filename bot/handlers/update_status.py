"""
/update_status FSM handler — moves a trader to a new lifecycle stage.
"""
import logging

import httpx
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from api import client as api
from states.trader_states import UpdateStatusStates

logger = logging.getLogger(__name__)
router = Router()

VALID_STATUSES = ["new", "registered", "funded", "active"]

status_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=s)] for s in VALID_STATUSES],
    resize_keyboard=True,
    one_time_keyboard=True,
)


@router.message(Command("update_status"))
async def cmd_update_status(message: Message, state: FSMContext):
    await state.set_state(UpdateStatusStates.waiting_for_trader_id)
    await message.answer(
        "🔄 <b>Update Trader Status</b>\n\nStep 1/2 — Enter the trader's <b>ID</b>:",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(UpdateStatusStates.waiting_for_trader_id)
async def process_trader_id(message: Message, state: FSMContext):
    trader_id = message.text.strip()
    if len(trader_id) != 24:
        await message.answer("⚠️ That doesn't look like a valid ID (should be 24 characters). Try again:")
        return
    await state.update_data(trader_id=trader_id)
    await state.set_state(UpdateStatusStates.waiting_for_status)
    await message.answer(
        "Step 2/2 — Select the <b>new lifecycle stage</b>:",
        parse_mode="HTML",
        reply_markup=status_keyboard,
    )


@router.message(UpdateStatusStates.waiting_for_status)
async def process_new_status(message: Message, state: FSMContext):
    new_status = message.text.strip().lower()
    if new_status not in VALID_STATUSES:
        await message.answer(
            f"⚠️ Please pick one of: {', '.join(VALID_STATUSES)}",
            reply_markup=status_keyboard,
        )
        return

    data = await state.get_data()
    await state.clear()

    try:
        trader = await api.update_status(data["trader_id"], new_status)
        await message.answer(
            f"✅ <b>Status updated!</b>\n\n"
            f"👤 {trader['name']} is now <b>{trader['status'].upper()}</b>",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardRemove(),
        )
    except httpx.HTTPStatusError as e:
        detail = e.response.json().get("detail", "Unknown error")
        await message.answer(f"❌ Error: {detail}")
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        await message.answer("❌ An unexpected error occurred.")
