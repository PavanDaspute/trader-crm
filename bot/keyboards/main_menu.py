"""
Shared inline keyboard: main navigation menu.
Shown after every successful bot action — keeps teams moving fast.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Four quick-action buttons shown after any successful operation."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Add Trader",    callback_data="nav:add_trader"),
            InlineKeyboardButton(text="🔄 Update Status", callback_data="nav:update_status"),
        ],
        [
            InlineKeyboardButton(text="💰 Add Deposit",  callback_data="nav:deposit"),
            InlineKeyboardButton(text="📊 View Stats",   callback_data="nav:stats"),
        ],
    ])


MENU_TEXT = "🔧 <b>What would you like to do next?</b>"
