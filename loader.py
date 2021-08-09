from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.callback_data import CallbackData


from config import Config

config = Config()
mytoken=config.token

# Callback for inline keyboard
run_commands = CallbackData('comand_run', 'action', 'id_', )
edit_commands = CallbackData('edit_commands', 'action')
del_commands = CallbackData('del_commands', 'action', 'id_')
sure_del = CallbackData('sure', 'confirm', 'action', 'id_')
go_next = CallbackData('go', 'action')

# bot = Bot(token=mytoken, parse_mode=types.ParseMode.Markdown)
bot = Bot(token=mytoken,)
Storage = MemoryStorage()
dp = Dispatcher(bot, storage=Storage)
