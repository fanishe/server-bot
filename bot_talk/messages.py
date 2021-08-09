'''
Пока не знаю как это дело употребить
Все обработчики лежат в папке handlers
и исходя из логики, отправляются те или иные сообщения
Возможно тут будут лежать методы которые шлют сообщения
Например:
    ---handlers/message_handler.py---
    from bot_talk.messages import send_commands
      ...
    if msg.text == 'run_command':
        ...
        await send_commands()

    А тут будут лежать какие-то константные методы, или фразы, которые бот будет отправлять
'''
import logging
from subprocess import check_output
from aiogram import types

from loader import dp
from handlers import incoming_message_handler
import keyboard as kb

# async def set_default_messages(disp):
#     ''' Main func
#          Gglavnaya upravlyaushaja func,
#          Kotoraya regitririuet vse ostalnuie funcs
#     '''
#     disp.register_message_handler(incoming_message_handler)

# async def incoming_message_handler(msg: types.Message):
#     if msg.text == 'run commands':
#         answ = 'Выберите команду'
#         inl_kb = await kb.get_cmd_for_ikb()

#         await msg.answer(answ, reply_markup=inl_kb)
#     else:
#         answ = 'try again'
#         await msg.answer(answ,)

