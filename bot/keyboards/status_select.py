"""
Lifecycle status selection keyboard.
Highlights the suggested next stage for the selected trader.
"""
from typing import Optional

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

LIFECYCLE_ORDER = ["new", "registered", "funded", "active"]

STATUS_LABEL = {
    "new":        "🆕 New",
    "registered": "📝 Registered",
    "funded":     "💰 Funded",
    "active":     "🚀 Active",
}


def suggested_next(current_status: str) -> Optional[str]:
    """Return the next stage in the lifecycle, or None if already active."""
    try:
        idx = LIFECYCLE_ORDER.index(current_status)
        return LIFECYCLE_ORDER[idx + 1] if idx + 1 < len(LIFECYCLE_ORDER) else None
    except ValueError:
        return None


def status_select_keyboard(current_status: str) -> InlineKeyboardMarkup:
    """
    Show all four stages. Mark the suggested next one with ✨.
    Skipping stages is allowed but visually discouraged.
    """
    next_stage = suggested_next(current_status)
    buttons = []
    for s in LIFECYCLE_ORDER:
        label = STATUS_LABEL[s]
        if s == next_stage:
            label = f"✨ {label} (Suggested)"
        elif s == current_status:
            label = f"• {label} (Current)"
        buttons.append([
            InlineKeyboardButton(text=label, callback_data=f"set_status:{s}"),
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)



