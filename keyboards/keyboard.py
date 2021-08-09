import logging
from collections import namedtuple

from aiogram.types import ReplyKeyboardMarkup as rkb
from aiogram.types import InlineKeyboardMarkup as ikb
from aiogram.types import InlineKeyboardButton as ibtn
from aiogram.utils.callback_data import CallbackData

import database.comandos as cmd
from loader import dp, config,  run_commands, edit_commands, del_commands, sure_del, go_next

def start_kb():
    kb = rkb(resize_keyboard=True)
    buttons = [
            config.get_param('buttons', 'run_commands'),
            'Torrent',
            'Link download',
            config.get_param('buttons', 'books'),
            ]
    kb.add(*buttons)
    return kb

async def get_cmd_for_ikb(edit=False):
    ''' Хороший пример кода для callback_data
        https://gist.github.com/Birdi7/d5249ae88015a1384b7200dcb51e85ce
    '''
    actions = 'run_command' if edit else 'edit_command'
    result = await cmd.get_all_scripts_from_db()
    logging.info(f"Query result - {result}")

    Script = namedtuple('Script', 'script_id name cmd comment editable')
    script_list = [Script(*res) for res in result]

    kb = ikb()
    for script in script_list:
        logging.info(f"Script for Inline Keyboard - {script}")
        cb_data = run_commands.new(action=actions,
                                id_=script.script_id,
                                )
        t = f'➡️ {script.name}'
        kb.add(ibtn(text=t, callback_data=cb_data))

    if not edit:
        kb.add(ibtn(text='⚙️ settings',
               callback_data=edit_commands.new(action='settings',)))
    else:
        kb.add(
                ibtn(text='⛔️ cancel', callback_data=edit_commands.new(action='cancel')),
                )
    return kb

async def kb_for_edit_commands():
    kb = ikb()
    kb.add(
            ibtn(text='➕ add new', callback_data=edit_commands.new(action='add_new')),
            ibtn(text='edit commands', callback_data=edit_commands.new(action='edit_commands')),
            ibtn(text='‼️ del cmd', callback_data=edit_commands.new(action='del_command')),
            ibtn(text='⛔️ cancel', callback_data=edit_commands.new(action='cancel')),
            )
    return kb

async def cancel_ibtn():
    kb = ikb()
    kb.add(
            ibtn(text='⛔️ cancel', callback_data=edit_commands.new(action='cancel')),
            )
    return kb

async def get_commands_for_del():
    kb = ikb()
    result = await cmd.get_all_scripts_from_db()
    Script = namedtuple('Script', 'script_id name cmd comment editable')
    script_list = [Script(*res) for res in result]

    for script in script_list:
        cb_data = del_commands.new(action='show', id_=script.script_id)
        if script.editable == int(0):
            continue
        kb.add(ibtn(
                text = '🗑 ' + script.name,
                callback_data=cb_data
                ))
    kb.add(
            ibtn(text='⛔️ cancel', callback_data=edit_commands.new(action='cancel')),
            )
    return kb

# sure_del('sure', 'confirm', 'action', 'id_')
async def yes_no_for_del(script_id):
    kb = ikb()
    kb.add(ibtn(text = '✅ Yes', callback_data=sure_del.new(confirm='yes', action='delete', id_=script_id)))
    kb.add(ibtn(text = '⛔️ No', callback_data=sure_del.new(confirm='no', action='cancel', id_='null')))
    return kb

# go_next = CallbackData('go', 'action')
async def get_go_next_ikb():
    kb = ikb(row_width=2)
    kb.add(
            ibtn(text='◀️',callback_data=go_next.new(action='go_prev')),
            ibtn(text='▶️',callback_data=go_next.new(action='go_next')),
            )
    return kb

