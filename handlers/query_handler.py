'''
TODO: Commands for shell:
    [v] sudo /hdd/gh/server-bot/scripts/ncrights.sh
    [v] sudo /hdd/gh/server-bot/scripts/calibre.sh
    [v] calibrescan.sh
    [ ] ?? fail2ban
        - Not installed yet
    [v] add country to whitelist
'''
import os
from subprocess import check_output
import typing
import logging

from aiogram.utils.callback_data import CallbackData
from aiogram import types

from loader import dp, run_commands, edit_commands, del_commands, sure_del
from scripts import full_output_to_user, scan_books
from database.comandos import delete_script, get_script_name_by_id, get_script_command_by_id
from keyboards import (
        kb_for_edit_commands,
        get_cmd_for_ikb,
        cancel_ibtn,
        get_commands_for_del,
        yes_no_for_del
        )


# del_commands = CallbackData('del_commands', 'id_')
@dp.callback_query_handler(del_commands .filter())
async def confirm(query: types.CallbackQuery, callback_data: dict):
    action = callback_data.get('action')
    msg = 'Are you sure?'
    inl_kb = await yes_no_for_del(callback_data.get('id_'))

    await query.message.edit_text(msg, reply_markup=inl_kb)
    await query.answer()

# sure_del('sure', 'confirm', 'action', 'id_')
@dp.callback_query_handler(sure_del.filter())
async def yes_or_no(query: types.CallbackQuery, callback_data: dict):
    confirm = callback_data.get('confirm')
    if confirm == 'yes':
        try:
            logging.info(f"CALLBACKDATA - {callback_data}")
            script_id = callback_data['id_']
            res = await get_script_name_by_id(script_id )
            await delete_script(script_id)
            await query.message.edit_text(f'\tDELETED\n```{res}```', parse_mode='MarkdownV2')
            await query.answer()
        except Exception as err:
            await query.message.reply(
                    f'ERROR:\n```{err}```\n\nTry again',
                    parse_mode='MarkdownV2'
                    )

    elif confirm == 'no':
        msg = 'edit commands were canceled'
        inl_kb = await get_cmd_for_ikb()
        await query.message.edit_text(msg, reply_markup=inl_kb)
        await query.answer()

# edit_commands = CallbackData('edit_commands', 'action')
@dp.callback_query_handler(edit_commands.filter())
async def edit_command_handler(query: types.CallbackQuery, callback_data: dict):
    action = callback_data.get('action')
    if action == 'settings':
        msg = 'choose your destiny\nРедактирование команд пока не работает'
        inl_kb = await kb_for_edit_commands()

    elif action == 'add_new':
        msg = 'Type new command separated by new line \ncommand name \n command \ncomment (optionally)\n/add_cmd'
        inl_kb = await cancel_ibtn()

    elif action == 'edit_commands':
        msg = 'Этот функционал еще не реализован'
        # inl_kb = await get_cmd_for_ikb(edit=True)
        inl_kb = await get_cmd_for_ikb()

    elif action == 'del_command':
        msg = 'Chose command to delete'
        inl_kb = await get_commands_for_del()

    elif action == 'cancel':
        msg = 'edit commands were canceled'
        inl_kb = await get_cmd_for_ikb()

    else:
        pass

    await query.message.edit_text(msg, reply_markup=inl_kb)
    await query.answer()

# run_commands = CallbackData('comand_run', 'action', 'id_')
@dp.callback_query_handler(run_commands.filter())
async def commands_handler(query: types.CallbackQuery, callback_data: dict):
    action = callback_data.get('action')

    logging.warning(f"CALBACK_DATA - {callback_data}")
    unix_cmd = await get_script_command_by_id(callback_data.get('id_'))
    unix_cmd  = unix_cmd[0][0]

    logging.info(f"UNIX_CMD - {unix_cmd}")

    if unix_cmd == 'sudo /hdd/gh/server-bot/scripts/calibrescan.sh':
        await scan_books(query, unix_cmd)

    elif unix_cmd == 'add_to_white_list':
        msg = 'Чтобы добавить новую страну введите /whitelist_add'

        await query.message.edit_text(msg,)
        await query.answer()

    else:
        await full_output_to_user(query, unix_cmd)
        await query.answer()
