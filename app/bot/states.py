from aiogram.fsm.state import StatesGroup, State


class WalletStates(StatesGroup):
    waiting_amount = State()


class TicketStates(StatesGroup):
    waiting_category = State()
    waiting_text = State()


class AdminStates(StatesGroup):
    waiting_user_search = State()
    waiting_balance = State()
    waiting_setting_value = State()
    waiting_card_number = State()
    waiting_card_holder = State()
    waiting_payment_instructions = State()
    waiting_min_topup = State()
    waiting_max_topup = State()
