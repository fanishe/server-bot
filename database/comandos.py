import logging
import asyncio
import aiosqlite
from collections.abc import Iterable

from loader import config

# [v] Create database, table scripts
#     id, name, command, comment, editable
# [v] Write script, that put into table script from TG
    # [v] foo that inserts data
    # [v] TG methods that ask user to scripts
# [v] Get data from table scripts
# [v] Send inline buttons with name of scipts
#     callbak_data id:name
# [v] get command from table
# [v] run command
# [v] send output to TG



DB = config.get_param('commands', 'database')

def get_not_iterable(result):
    logging.info(f"Start strip {result}")
    while isinstance(result, Iterable):
        result = result[0]
        logging.info(f"Stripped - {result}")
    return result

async def put_new_script(name, cmd, comment=None, editable=0):
    q = '''
        insert into scripts (script_name, command, comment, editable)
        values(?, ?, ?, ?)
    '''
    commentary = comment or 'null'
    args = (name, cmd, commentary, editable)
    await run_query(q, args)

async def put_new_script_with_return_row(name, cmd, comment=None, editable=1):
    q = '''
        insert into scripts (script_name, command, comment, editable)
        values(?, ?, ?, ?)
        returning *
    '''
    commentary = comment or 'null'
    args = (name, cmd, commentary, editable)
    res = await run_select(q, args)

async def delete_script(script_id):
    q = 'delete from scripts where script_id = ?'
    args = script_id,
    await run_query(q, args)

async def get_script_name_by_id(script_id):
    q = 'select script_name from scripts where script_id = ?'
    return  await run_select(q, (script_id,))

async def get_script_command_by_id(script_id):
    q = 'select command from scripts where script_id = ?'
    return await run_select(q, (script_id,))

async def get_all_scripts_from_db():
    q = 'select * from scripts'
    return await run_select(q)

async def get_script_from_db(name):
    q = '''
        select * from scripts
        where script_name = (?)
    '''
    args = (name, )
    res = await run_select(q, args)

async def create_table_scripts():
    q = '''
        CREATE TABLE IF NOT EXISTS
	scripts (script_id INTEGER PRIMARY KEY,
                script_name name TEXT NOT NULL,
                command TEXT NOT NULL,
                comment TEXT DEFAULT 'null',
                editable BOOL DEFAULT FALSE
                )
    '''
    await run_query(q)

async def run_query(query, vals=None):
    async with aiosqlite.connect(DB) as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, vals)
            await conn.commit()

async def run_select(query, vals=None):
    async with aiosqlite.connect(DB) as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, vals)
            await conn.commit()
            res = await cur.fetchall()
            return res



# if __name__ == '__main__':
    # asyncio.run(delete_script(4))
    # pass
    # asyncio.run(create_table_scripts())
    # asyncio.run(get_script_from_db('ls'))
    # asyncio.run(put_new_script('lls', 'ls',))
