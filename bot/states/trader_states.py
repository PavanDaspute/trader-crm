"""
FSM state groups for all multi-step bot conversations.
"""
from aiogram.fsm.state import State, StatesGroup


class AddTraderStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_contact = State()
    waiting_for_source = State()


class UpdateStatusStates(StatesGroup):
    waiting_for_trader_id = State()
    waiting_for_status = State()


class DepositStates(StatesGroup):
    waiting_for_trader_id = State()
    waiting_for_amount = State()
