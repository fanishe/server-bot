from aiogram import Dispatcher
from .message_handler import incoming_message_handler
from .query_handler import dp

def setup(dp: Dispatcher):
    dp.register_message_handler(incoming_message_handler)

