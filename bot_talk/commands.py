import logging
import requests
from aiogram.types import Message
from aiogram.dispatcher import FSMContext
from subprocess import check_output

from loader import config
from keyboards import start_kb, get_cmd_for_ikb
from states.state import AddNewCommand, WhiteListAdd
from database.comandos import put_new_script
from scripts import full_output_to_user

_CMD = config.get_param('commands', 'whitelist_add')

async def cmd_start(message: Message):
    ''' Точка входа в бота, тут можно вставить необходимые настройки, которые нужны перед стартом
    '''
    msg = 'Start message'
    await message.answer(msg, reply_markup=start_kb())

async def cmd_help(message: Message):
    ''' Help message for bot
    '''
    msg = 'Help message'
    await message.answer(msg)

async def add_new_command(msg: Message, state: FSMContext):
    ''' Старт добавления команды'''
    await msg.answer(
            'С новой строки напиши\n'
            'Имя команды\n'
            'Сама команда\n'
            'Комментарий, если нужен\n'
            'Если изменяемая команда - 1, если нет - 0'
            )
    await AddNewCommand.fulltext.set()

async def fin_add_new_command(msg: Message, state: FSMContext):
    try:
        data = msg.text.split('\n')
        await put_new_script(*data)
        ikb = await get_cmd_for_ikb()
        await msg.answer(f'Command was added', reply_markup=ikb)
        await state.finish()
    except Exception as err:
        await msg.reply(
                f'ERROR:\n```{err}```\n\nTry again\nOr type /cancel',
                parse_mode='MarkdownV2'
                )
        return

async def whitelist_add(msg: Message, state: FSMContext):
    ''' Старт добавления команды
        http://www.ipdeny.com/ipblocks/data/countries/ua.zone
    '''
    await msg.answer(
            'Для начала поищите [код страны тут](http://www.tigir.com/domains.htm)\n'
            'После этого введите необходимый код в сообщении\n'
            'Если несколько стран, то каждую надо вводить с новой строки\n'
            'Или нажмите /cancel для отмены\n',
            parse_mode='MarkdownV2')
    await WhiteListAdd.domain.set()

async def fin_whitelist_add(msg: Message, state: FSMContext):
    ''' Получить код страны
            сделать запрос через requests
            http://www.ipdeny.com/ipblocks/data/countries/mu.zone
            если ответ 200:
                вставить страну в команду
                выполнить
            если 404:
                Ответить, что такой страны не существует
                Спробуй ще или /cancel
    '''
    for zone in msg.text.split('\n'):
        ipdeny = f'http://www.ipdeny.com/ipblocks/data/countries/{zone}.zone'
        r = requests.get(ipdeny,)
        if r.status_code != 200:
            await msg.answer(
                    f'Country Code: `{zone}` incorrect\n'
                    'Try again or type /cancel',
                    parse_mode='MarkdownV2'
                    )
            return
        else:
            try:
                cmd = CMD.format(zone)
                await full_output_to_user(msg, cmd, edit=False)

            except Exception as err:
                await msg.reply(
                        f'ERROR:\n```{err}```\n\nTry again\nOr type /cancel',
                        parse_mode='MarkdownV2'
                        )
                return


    await state.finish()

async def cancel(msg: Message, state: FSMContext):
    await msg.answer('Действие отменено')
    await state.finish()
