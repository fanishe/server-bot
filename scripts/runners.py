import asyncio
import aiosqlite
import subprocess
from subprocess import check_output
from collections import namedtuple
import logging

from aiogram import types

from loader import config
from database import run_select


_DB = config.get_param('calibre', 'database')

async def full_output_to_user(back, command: str, edit=True):
    output = check_output(
            command,
            stderr=subprocess.STDOUT,
            shell=True)
    logging.info(f" \nOUTPUT: {output}")

    output = ' \n '.join(
            output.decode().split('\n')
            ).rstrip(' \n ')

    logging.warn(f"\n\n FORMATTED - {(output, )}\n\n")
    formatted = f'```{output}```'

    if isinstance(back, types.CallbackQuery):
        if edit:
            await back.message.edit_text(formatted, parse_mode='MarkdownV2')
        else:
            await back.message.answer(formatted, parse_mode='MarkdownV2')

    elif isinstance(back, types.Message):
        if edit:
            await back.edit_text(formatted, parse_mode='MarkdownV2')
        else:
            await back.answer(formatted, parse_mode='MarkdownV2')

async def scan_books(cb: types.CallbackQuery, command: str):
    ''' Запускает команду на исполнение
        sudo /path/to/server-bot/scripts/calibrescan.sh
        ВОзвращает вывод:
        qt.gui.icc: Unsupported ICC profile class 70727472
        The following books were not added as they already exist in the database (see --duplicates option):
          ...
        Added book ids: 199, 200, 201, ...
    '''
    # command = 'sudo /path/to/server-bot/scripts/calibrescan.sh'
    output = check_output(
            command,
            stderr=subprocess.STDOUT,
            shell=True)
    if output:
        outputs = output.decode().split('\n')
        for line in outputs:
            if 'Added book' in line:
                await _parse_digits(cb, line)
    else:
        msg = 'Nothing to scan'
        await cb.message.edit_text(
                msg,
                )

async def _parse_digits(cb: types.CallbackQuery, line: list):
    '''
        Added book ids: 199, 200, 201, ...
    '''
    str_digits = line.split('ids:')[1].split(',')
    nums = [ num.strip() for num in str_digits ]

    res = await _get_data_from_books_db(nums)
    msg = '*Added books:*\n'
    for book in res:
        msg += f'`{book[0]}`\n'

    await cb.message.edit_text(
            msg,
            parse_mode='MarkdownV2'
            )

async def _get_data_from_books_db(numbers):
    q = '''
        select title from books
        where id in (
    ''' + '?, ' * len(numbers[:-1])
    q += '? );'
    res = await run_select(_DB, q, numbers)
    return res
