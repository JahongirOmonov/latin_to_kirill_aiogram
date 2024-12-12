from aiogram.fsm.state import StatesGroup, State


class Messages(StatesGroup):
    messages_for_user = State()

class MessageStates(StatesGroup):
    id_of_user = State()
    message_for_user = State()

class SmsForAdmin(StatesGroup):
    sms = State()

class InfoUser(StatesGroup):
    id_of_user = State()

class ArchiveState(StatesGroup):
    id_of_user = State()