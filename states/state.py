from aiogram.dispatcher.filters.state import State, StatesGroup


class AddNewCommand(StatesGroup):
    fulltext = State()

class WhiteListAdd(StatesGroup):
    domain = State()
