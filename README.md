# Server bot

# Sources:
- [Знакомство с aiogram](https://mastergroosha.github.io/telegram-tutorial-2/quickstart/)
    - [Форматирование сообщений](https://mastergroosha.github.io/telegram-tutorial-2/messages/)
- [[OF.DOC.] Coroutines and Tasks](https://docs.python.org/3/library/asyncio-task.html)
- [aiogram examples](https://github.com/aiogram/aiogram/tree/dev-2.x/examples)
- [aiogram tutor](https://docs.aiogram.dev/en/latest/quick_start.html)

## Link downloader wrom WA
- [Script to download files in a async way, using Python asyncio](https://gist.github.com/darwing1210/c9ff8e3af8ba832e38e6e6e347d9047a)
- [[OF.DOC.] Coroutines and Tasks](https://docs.python.org/3/library/asyncio-task.html#coroutines)

```python
    def link_worker(self, sms):
        """обработчик ссылок"""
        user_phone, _ = basic.user_info(sms)

        if sms.getType() == 'text':
            message = sms.getBody()
        elif sms.getType() == 'media':
            message = sms.matched_text

        logging.info(
            'User_ID = {} sent link - {}'
            .format(user_phone, message)
            )
        # Check if url is correct...
        text, file_id = basic.check_url(message, user_phone, sms)

        self.send_message(text, user_phone, sms)
        res = self.link_download(user_phone, file_id, sms)

        if res == 0: # download success
            file_info = self.db_bot.get_file_for_task(1, file_id)
            filename = file_info[4]

            self.upload_to_athena(filename, file_id)
            self.wait_answer_from_athena(filename, file_id, user_phone, sms)
            self.delete_file(file_id)

```

## output of scan books

```
➜ docker exec -ti calibre-web  calibredb add /scan --add -r --with-library  /books                              qt.gui.icc: Unsupported ICC profile class 70727472
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

```
# Кнопка edit_commands:
#     add_command: DONE
#         enter command, name, comment, if editable put 1 else 0
#         put inl_btn: cancel
#         if allright: put new command into DB
#         not work! 
#         /add_cmd - and after that put new command
#     edit_commands: NOT YET
#         select command to edit: select editable commands from DB to inl_kb
#         tap on any command: what exactly you whant to change: show inl_kb: command, name, comment, all
#         enter new value: check if value correct
#         edit command in DB
#         answer with inl_kb commands
#     del_command: DONE
#         select command to delete: show editable commands from DB
#         after command selected: are you sure? inl_kb: yes, no
#     cancel:
#         go back to comands list
```
Чтобы команда исполнялась без пароля и это было более-менее сесурно надо:
1. записать команду в shell скрипт и сохранить ее `echo sudo some cmd -run`
1. Присвить права на исполнение только руту `sudo chown root:root /path/to/script.sh && sudo chmod 700 /path/to/script.sh`
1. Выполнить команду `sudo visudo` с помощью Nano модно будет редактировать документ
1. В конец добавить строку: `fantomas  ALL=(ALL) NOPASSWD: /path/to/script.sh`
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
