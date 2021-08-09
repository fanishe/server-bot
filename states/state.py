from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext


class AddNewCommand(StatesGroup):
    fulltext = State()

class WhiteListAdd(StatesGroup):
    domain = State()
