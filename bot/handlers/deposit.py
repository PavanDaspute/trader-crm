"""
/deposit FSM handler — records a deposit for a trader.
"""
import logging

import httpx
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from api import client as api
from states.trader_states import DepositStates

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("deposit"))
async def cmd_deposit(message: Message, state: FSMContext):
    await state.set_state(DepositStates.waiting_for_trader_id)
    await message.answer(
        "💰 <b>Record Trader Deposit</b>\n\nStep 1/2 — Enter the trader's <b>ID</b>:",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(DepositStates.waiting_for_trader_id)
async def process_trader_id(message: Message, state: FSMContext):
    trader_id = message.text.strip()
    if len(trader_id) != 24:
        await message.answer("⚠️ Invalid ID format. Please enter the 24-character trader ID:")
        return
    await state.update_data(trader_id=trader_id)
    await state.set_state(DepositStates.waiting_for_amount)
    await message.answer("Step 2/2 — Enter the <b>deposit amount</b> (USD):", parse_mode="HTML")


@router.message(DepositStates.waiting_for_amount)
async def process_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.strip().replace(",", ""))
        if amount <= 0:
            raise ValueError("Amount must be positive")
    except ValueError:
        await message.answer("⚠️ Please enter a valid positive number (e.g. 500 or 1250.50):")
        return

    data = await state.get_data()
    await state.clear()

    try:
        trader = await api.add_deposit(data["trader_id"], amount)
        await message.answer(
            f"✅ <b>Deposit recorded!</b>\n\n"
            f"👤 Trader: {trader['name']}\n"
            f"💵 Added: <b>${amount:,.2f}</b>\n"
            f"💼 Total Deposits: <b>${trader['total_deposit']:,.2f}</b>",
            parse_mode="HTML",
        )
    except httpx.HTTPStatusError as e:
        detail = e.response.json().get("detail", "Unknown error")
        await message.answer(f"❌ Error: {detail}")
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        await message.answer("❌ An unexpected error occurred.")
