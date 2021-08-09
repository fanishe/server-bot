'''
TODO: Скан книг:
    [v] Сделать запрос в БД metadta.db
    [v] Получить список книг, в которых не все поля заполнены
    [v] Послать смс в котором указаны эти книги как ссылка для редактирования
        https://books.domain/calibre/book/<ID> - show
    [v] Показать первые ?? (5) ?? книг и внизу инлайн кнопки
        [v] > След 5 книг
        [v] < Пред 5, если есть
'''
import logging
import asyncio
import aiosqlite

from loader import config

DB = config.get_param('calibre', 'database')

class bidirectional_iterator(object):
    ''' объект, который возвращает 5 следующих
        и 5 предыдущих книг
    '''
    def __init__(self, collection):
        self.collection = collection
        self.index = 0
        self.step = 5
        self.start = 0
        self.fin = 5
        self.prev_res  = None
        self.next_res  = None

    def reset(self):
        ''' Сброс до заводских настроек
            Используется во время нового вызова команды Books
        '''
        self.__init__(self.collection)

    def __next(self):
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

    def __prev(self):
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

    def next(self):
        res = self.__next()
        if res != self.next_res:
            return res
        else:
            res = self.__next()
            return res

    def prev(self):
        res = self.__prev()
        if res != self.prev_res:
            return res
        else:
            res = self.__prev()
            return res

async def books_info():
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
    result = await run_select(q)
    books_res = []
    num = 0
    for res in result:
        if None in res:
            num += 1
            id_book_name = (num, res[0], res[1])
            books_res.append(id_book_name)

    # Возвращает объект, который имеет два вызова
    # next() следующие 5
    # и prev() предыдущие 5 книг из списка
    bi = bidirectional_iterator(books_res)
    return bi

async def run_select(query, vals=None):
    async with aiosqlite.connect(DB) as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, vals)
            await conn.commit()
            res = await cur.fetchall()
            return res
