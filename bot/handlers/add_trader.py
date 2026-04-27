"""
/add_trader FSM handler — collects name, contact, and source.
After success: shows smart navigation inline keyboard.
"""
import logging

import httpx
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery, Message,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
)

from api import client as api
from keyboards.main_menu import main_menu_keyboard, MENU_TEXT
from states.trader_states import AddTraderStates

logger = logging.getLogger(__name__)
router = Router()

VALID_SOURCES = ["Telegram", "Ads", "Referral", "Organic", "Other"]

source_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=s)] for s in VALID_SOURCES],
    resize_keyboard=True,
    one_time_keyboard=True,
)


async def _start_add_trader_flow(target, state: FSMContext):
    """Shared entry point used by both /add_trader command and nav button."""
    await state.set_state(AddTraderStates.waiting_for_name)
    text = (
        "📝 <b>New Trader Registration</b>\n\n"
        "Step 1/3 — Enter the trader's <b>full name</b>:"
    )
    if hasattr(target, "message"):
        # Called from a callback
        await target.message.edit_text(text, parse_mode="HTML")
    else:
        await target.answer(text, parse_mode="HTML", reply_markup=ReplyKeyboardRemove())


@router.message(Command("add_trader"))
async def cmd_add_trader(message: Message, state: FSMContext):
    await _start_add_trader_flow(message, state)


@router.callback_query(F.data == "nav:add_trader")
async def nav_add_trader(callback: CallbackQuery, state: FSMContext):
    await _start_add_trader_flow(callback, state)


@router.message(AddTraderStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("⚠️ Name must be at least 2 characters. Try again:")
        return
    await state.update_data(name=name)
    await state.set_state(AddTraderStates.waiting_for_contact)
    await message.answer(
        "Step 2/3 — Enter the trader's <b>contact</b> (email, phone, or Telegram @handle):",
        parse_mode="HTML",
    )


@router.message(AddTraderStates.waiting_for_contact)
async def process_contact(message: Message, state: FSMContext):
    contact = message.text.strip()
    if len(contact) < 3:
        await message.answer("⚠️ Contact seems too short. Please enter a valid email, phone, or handle:")
        return
    await state.update_data(contact=contact)
    await state.set_state(AddTraderStates.waiting_for_source)
    await message.answer(
        "Step 3/3 — How did this trader <b>find us</b>? Pick a source:",
        parse_mode="HTML",
        reply_markup=source_keyboard,
    )


@router.message(AddTraderStates.waiting_for_source)
async def process_source(message: Message, state: FSMContext):
    source = message.text.strip()
    if source not in VALID_SOURCES:
        await message.answer(
            f"⚠️ Please pick one of: {', '.join(VALID_SOURCES)}",
            reply_markup=source_keyboard,
        )
        return

    data = await state.get_data()
    await state.clear()

    try:
        trader = await api.create_trader(data["name"], data["contact"], source)
        await message.answer(
            f"✅ <b>Trader Added Successfully!</b>\n\n"
            f"👤 <b>{trader['name']}</b>\n"
            f"📞 Contact: {trader['contact']}\n"
            f"📡 Source: {trader['source']}\n"
            f"🆕 Status: <b>NEW</b>\n"
            f"🆔 ID: <code>{trader['id']}</code>\n\n"
            f"{MENU_TEXT}",
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(),
        )
    except httpx.HTTPStatusError as e:
        logger.error("Failed to create trader: %s", e.response.text)
        await message.answer(
            "❌ Failed to create trader. Please try again later.\n\n" + MENU_TEXT,
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(),
        )
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        await message.answer("❌ An unexpected error occurred.")
    finally:
        # Always hide the reply keyboard
        await message.answer("‎", reply_markup=ReplyKeyboardRemove())
