import asyncio
import logging
from aiogram.types import Message, CallbackQuery
from collections import namedtuple

from keyboards import get_cmd_for_ikb, get_go_next_ikb
from scripts import books_info
from loader import dp, config, go_next


RUN_COMMANDS = config.get_param('buttons', 'run_commands')
BOOKS = config.get_param('buttons', 'Books')
URL = config.get_param('calibre', 'url')

loop = asyncio.get_event_loop()
GEN = loop.run_until_complete(books_info())

async def incoming_message_handler(msg: Message):
    ''' Обработчик всех входящих сообщений
    '''
    if msg.text == RUN_COMMANDS:
        answ = 'Выберите команду'
        inl_kb = await get_cmd_for_ikb()

        await msg.answer(answ, reply_markup=inl_kb)

    elif msg.text == BOOKS:
        GEN.reset()
        await send_book_info(msg, GEN.next())

    else:
        answ = 'try again'
        await msg.answer(answ,)

async def send_book_info(msg: Message, books_data: list, edit:bool=False):
    ''' Отправить полученный список книг
    [(1, 1, 'Политика'), (2, 3, 'Великий канцлер'), ...]
    '''
    Book = namedtuple('Book', 'num id_ title')
    books = [Book(*lst) for lst in books_data]

    sms = 'Книги для редактирования:\n'
    for book in books:
        sms += f'{book.num}) <a href="{URL}{book.id_}">{book.title}</a>\n'
    inl_kb = await get_go_next_ikb()

    if edit:
        await msg.edit_text(sms,reply_markup=inl_kb, parse_mode='HTML')
    else:
        await msg.answer(sms,reply_markup=inl_kb, parse_mode='HTML')

# async def commands_handler(query: types.CallbackQuery, callback_data: dict):
@dp.callback_query_handler(go_next.filter())
async def book_handler(query: CallbackQuery, callback_data: dict):
    ''' Хэндлер, обрабатывающий елавиши вперед и назад
    '''
    action = callback_data.get('action')
    if action == 'go_next':
        try:
            data = GEN.next()
        except StopIteration:
            logging.info(f"StopIteration")
            await query.answer(text='Это была последняя позиция', show_alert=True)

        else:
            await send_book_info(query.message, data, edit=True)
            await query.answer()

    else:
        try:
            data = GEN.prev()
        except StopIteration:
            logging.info(f"StopIteration")
            await query.answer(text='Это была первая позиция', show_alert=True)
        else:
            await send_book_info(query.message, data, edit=True)
            await query.answer()
