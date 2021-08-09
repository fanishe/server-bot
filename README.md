# Server Bot
Бот для управления домашним сервером `Ubuntu 20.04`.

## Реализованные возможности:
### Запуск команд на сервере:
* Для этого создается локальная sqlite БД и в ней таблица `scripts`
* Можно добавлять, удалять команды черз инлайн кнопки, редактирование существующей команды пока не реализовано

### самые частые команды:
#### Добавление страны в белый список. 
На моем веб-сервере через ipset установлено ограниченное количество стран, которые имеют доступ. Благодаря этой команде, я могу в одно касание добавить новую страну, которой будет открыт доступ(Реализовано на случай путешествий, или длятельных командировок). Сами исполняемые скрипты могут запускать без запроса пароля для `sudo`.

#### Ручной запуск сканирования входящей папки с книгами для `calibre` 
Запускает `calibre` на сканирование папки в которую я добавил новые книги. В идеале это должно запускаться автоматически, но если по каким-то причинам этого не произошло, я могу сделать это вручную. После добавления книг, код подключается к БД `calibre` и достает от туда названия книг, которые были добавлены.

##### Результат работы сканирования
```
➜ docker exec -ti calibre-web  calibredb add /scan --add -r --with-library  /books

qt.gui.icc: Unsupported ICC profile class 70727472
The following books were not added as they already exist in the database (see --duplicates option):
  Один день Ивана Денисовича
    /scan/A_Solzhenitsyn_-_Odin_den_Ivana_Denisovicha.epub
  Архипелаг ГУЛАГ. 1918-1956: Опыт художественного исследования. Т. 2
    /scan/Солженицын - Архипелаг ГУЛАГ. 1918-1956_ Опыт художественного исследования. Т. 2.fb2
  Архипелаг ГУЛаг
    /scan/Архипелаг ГУЛАГ 3в1.fb2
  Архипелаг ГУЛАГ. 1918-1956: Опыт художественного исследования. Т. 1
    /scan/Солженицын - Архипелаг ГУЛАГ. 1918-1956_ Опыт художественного исследования. Т. 1.fb2
  Архипелаг ГУЛаг
    /scan/Солженицын Александр. Архипелаг ГУЛАГ.fb2
Added book ids: 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216
```
Я извлекаю последнюю строку, получаю id книг, которые были добавлены, и по ним получаю метаинформацию из БД `metadata.db`

Поиск по базе данных книг недооформленные книги.
Собрал единый SQL запрос:
```sql
SELECT
    id,
    title,
    (   SELECT bal.id|| ' '|| name 
        FROM books_authors_link AS bal 
        JOIN authors ON(author = authors.id) 
        WHERE book = books.id
    ) authors,
    (   SELECT lang.lang_code 
        FROM books_languages_link AS bll 
        JOIN languages AS lang ON (bll.lang_code = lang.id) 
        WHERE book = books.id 
    ) langauge,
    (   SELECT name 
        FROM publishers 
        WHERE publishers.id IN (
            SELECT publisher 
            FROM books_publishers_link 
            WHERE book=books.id)
    ) publisher,
    timestamp,
    (   SELECT name 
        FROM tags 
        WHERE tags.id IN (
            SELECT tag 
            FROM books_tags_link 
            WHERE book=books.id)
    ) tags,
    (select text FROM comments WHERE book=books.id) comments,
    sort,
    author_sort,
    pubdate
from books;
```
Если одно из полей пустое, значит надо оформить ее как полагается. Возвращает в чат первую пятерку книг, оформленных как ссылки, чтобы я мог сразу приступить к найденной книге. Так же внизу присутствуют две инлайн кнопки, следующие 5 и предыдущие 5.

### В планах реализовать:
- Проверка статуса `fail2ban`
    > Возвращает список заблокированных ip аздресов
    > Возможность разблокировки этого адреса
- Слежение за сертификатами от `certbot`
    > При подзоде срока истечении сертификата, присылал сообщение с напоминанием, и инлайн кнопкой для запуска обновления сертификатов.
- Поиск на rutracker.org и взаимодействие с установленным `transmission`


## Выполнение команды без запрашивания пароля

Чтобы команда исполнялась без пароля и это было более-менее сесурно надо:
1. записать команду в shell скрипт и сохранить ее `echo sudo some cmd -run`
1. Присвить права на исполнение только руту `sudo chown root:root /path/to/script.sh && sudo chmod 700 /path/to/script.sh`
1. Выполнить команду `sudo visudo` с помощью Nano модно будет редактировать документ
1. В конец добавить строку: `username  ALL=(ALL) NOPASSWD: /path/to/script.sh`
    > Чтобы изменить Nano на другой редактор надо выполнить команду
    > ` sudo update-alternatives --config editor`
    ```
    There are 6 choices for the alternative editor (providing /usr/bin/editor).

      Selection    Path                Priority   Status
      ------------------------------------------------------------
      * 0            /bin/nano            40        auto mode
        1            /bin/ed             -100       manual mode
        2            /bin/nano            40        manual mode
        3            /usr/bin/mcedit      25        manual mode
        4            /usr/bin/nvim        30        manual mode
        5            /usr/bin/vim.basic   30        manual mode
        6            /usr/bin/vim.tiny    15        manual mode

      Press <enter> to keep the current choice[*], or type selection number: 4
      update-alternatives: using /usr/bin/nvim to provide /usr/bin/editor (editor) in manual mode
    ```
    > Выбрать редактор который нужен я выбрал 4
1. Сохранить и выйти
1. Передать боту на исполнение команду/путь к файлу `sudo /path/to/script.sh`
1. Добавил проверку `exit-code` - `echo $?` возвращает `0` если команда выполнена успешно
