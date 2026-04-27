"""
/start handler — introduces the bot with an inline main-menu keyboard.
"""
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.main_menu import main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 Welcome to <b>TraderCRM Bot</b> — your brokerage lifecycle assistant!\n\n"
        "Track leads, record deposits, and monitor conversion — all from Telegram.\n\n"
        "📋 <b>Choose an action:</b>",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(),
    )
