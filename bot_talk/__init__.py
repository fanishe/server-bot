from aiogram import Dispatcher
from states import *

from .commands import *

# from .messages import *

def setup(dp: Dispatcher):
    dp.register_message_handler(cmd_help, commands='help')
    dp.register_message_handler(cmd_start, commands='start')

    dp.register_message_handler(add_new_command, commands='add_cmd', state='*')
    dp.register_message_handler(whitelist_add, commands='whitelist_add', state='*')

    dp.register_message_handler(cancel, commands='cancel', state='*')

    dp.register_message_handler(fin_add_new_command, state=AddNewCommand.fulltext)
    dp.register_message_handler(fin_whitelist_add, state=WhiteListAdd.domain)
