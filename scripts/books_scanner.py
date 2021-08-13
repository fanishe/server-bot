'''
Скан книг:
    [v] Сделать запрос в БД metadta.db
    [v] Получить список книг, в которых не все поля заполнены
    [v] Послать смс в котором указаны эти книги как ссылка для редактирования
        https://books.domain/calibre/book/<ID> - show
    [v] Показать первые (регулируется в настройках, по умолчанию - 5) книг и внизу инлайн кнопки
        [v] > След 5 книг
        [v] < Пред 5, если есть
'''
import logging
import asyncio
import aiosqlite
from async_class import AsyncClass

from loader import config
from database import run_select

_DB = config.get_param('calibre', 'database')
_QUANT = int(config.get_param('calibre', 'show_books_quantity'))


class bidirectional_iterator(AsyncClass):
    ''' объект, который возвращает 5 следующих
        и 5 предыдущих книг
        Использовадась библиотека, которая создает асинхронный класс
        https://pypi.org/project/async-class/
    '''
    async def __ainit__(self):
        self.collection = await __class__._books_info()
        self.index = 0
        self.step = _QUANT
        self.start = 0
        self.fin = _QUANT
        self.prev_res  = None
        self.next_res  = None

    async def reset(self):
        ''' Сброс до заводских настроек
            Используется во время нового вызова команды Books
        '''
        await self.__ainit__()

    async def __next(self):
        ''' Следующая пятерка
            В случае если срез выходит за пределы списка,
            питон ввозвращает пустой список
            и вызвать StopIteration
            prev_pos нужен для self.prev()
            логика:
                вызвал next()
                увеличил старт и финал на шаг вперед
                если сразу нажать prev(),
                то он уменьшит счетчики и вернет тот же список,
                чтобы это избежать надо сохранить в переменную, текущую строку
                и при вызове prev() он сравнит строки, если они одинаковые,
                вызовет __prev() еще раз
                и тогда возвращает нужный список
                то же самое и с next() после prev(),
                поэтому для prev хранится состояние в self.prev_res
                а для next, - в self.next_res
        '''
        result = self.collection[self.start:self.fin]
        if not result:
            raise StopIteration

        self.prev_res = result
        self.start += self.step
        self.fin += self.step

        return result

    async def __prev(self):
        ''' Предыдущая пятерка
            сделать шаг назад
            если старт меньше нуля raise StopIteration
        '''
        self.start -= self.step
        self.fin -= self.step

        if self.start < 0:
            self.start += self.step
            self.fin += self.step
            raise StopIteration

        res = self.collection[self.start: self.fin]
        self.next_res = res
        return res

    async def next(self):
        res = await self.__next()
        if res != self.next_res:
            return res
        else:
            res = await self.__next()
            return res

    async def prev(self):
        res = await self.__prev()
        if res != self.prev_res:
            return res
        else:
            res = await self.__prev()
            return res

    @staticmethod
    async def _books_info():
        q = '''
            select
                id,
                title,
                (select bal.id|| ' '|| name FROM books_authors_link AS bal JOIN authors ON(author = authors.id) WHERE book = books.id) authors,
                (select lang.lang_code from books_languages_link as bll join languages as lang on (bll.lang_code = lang.id) WHERE book = books.id ) langauge,
                (select name FROM publishers WHERE publishers.id IN (SELECT publisher from books_publishers_link WHERE book=books.id)) publisher,
                timestamp,
                (select name FROM tags WHERE tags.id IN (SELECT tag from books_tags_link WHERE book=books.id)) tags,
                (select text FROM comments WHERE book=books.id) comments,
                sort,
                author_sort,
                pubdate
            from books;
        '''
        result = await run_select(_DB, q)
        books_res = []
        num = 0
        for res in result:
            if None in res:
                num += 1
                id_book_name = (num, res[0], res[1])
                books_res.append(id_book_name)

        # Возвращает список, с которыми потом работает bi
        return books_res


async def _test_bi():
    bi = await bidirectional_iterator()
    print(await bi.next())
    print(await bi.next())

    await bi.reset()

    print(await bi.next())
    print(await bi.next())
    print(await bi.prev())
    print(await bi.next())
    print(await bi.prev())

if __name__ == '__main__':
    async def run_select(db, query, vals=None):
        async with aiosqlite.connect(db) as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, vals)
                await conn.commit()
                res = await cur.fetchall()
                return res

    _loop = asyncio.new_event_loop()
    bi = _loop.run_until_complete(_test_bi())
