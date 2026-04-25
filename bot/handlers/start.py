"""
/start handler — introduces the bot and lists available commands.
"""
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 Welcome to <b>TraderCRM Bot</b> — your brokerage lifecycle assistant!\n\n"
        "📋 <b>Available commands:</b>\n"
        "  /add_trader — Register a new trader lead\n"
        "  /update_status — Move a trader to the next lifecycle stage\n"
        "  /deposit — Record a trader deposit\n"
        "  /stats — View platform KPIs\n\n"
        "Let's convert some traders! 🚀",
        parse_mode="HTML",
    )
