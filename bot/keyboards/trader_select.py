"""
Inline keyboard builder for trader selection.
Fetches recent traders from the backend and renders each as a button.
"""
from typing import Optional

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

STATUS_EMOJI = {
    "new":        "🆕",
    "registered": "📝",
    "funded":     "💰",
    "active":     "🚀",
}


def trader_select_keyboard(
    traders: list[dict],
    action: str,
    max_shown: int = 8,
) -> InlineKeyboardMarkup:
    """
    Build an inline keyboard where each button shows:
    '{emoji} Name ({STATUS})'

    action is embedded in callback_data so the handler knows what to do:
      e.g. 'select_trader:update_status:<trader_id>'
    """
    buttons = []
    for t in traders[:max_shown]:
        emoji = STATUS_EMOJI.get(t["status"], "👤")
        label = f"{emoji} {t['name']} ({t['status'].upper()})"
        buttons.append([
            InlineKeyboardButton(
                text=label,
                callback_data=f"select_trader:{action}:{t['id']}",
            )
        ])

    # Fallback row — manual ID entry
    buttons.append([
        InlineKeyboardButton(text="✏️ Enter ID manually", callback_data=f"select_trader:{action}:MANUAL"),
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def no_traders_keyboard() -> InlineKeyboardMarkup:
    """Shown when the trader list is empty."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Add First Trader", callback_data="nav:add_trader")],
    ])
