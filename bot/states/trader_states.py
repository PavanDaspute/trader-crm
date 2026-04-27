"""
FSM state groups for all multi-step bot conversations.
"""
from aiogram.fsm.state import State, StatesGroup


class AddTraderStates(StatesGroup):
    waiting_for_name    = State()
    waiting_for_contact = State()
    waiting_for_source  = State()


class UpdateStatusStates(StatesGroup):
    selecting_trader  = State()   # inline keyboard or manual ID
    manual_trader_id  = State()   # fallback: user types ID
    selecting_status  = State()   # inline status keyboard


class DepositStates(StatesGroup):
    selecting_trader  = State()   # inline keyboard or manual ID
    manual_trader_id  = State()   # fallback: user types ID
    waiting_for_amount = State()  # user types amount
