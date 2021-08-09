import logging
logging.basicConfig(
    format="%(asctime)s : %(filename)s : [LINE:%(lineno)d] : %(levelname)s : %(message)s",
    level=logging.DEBUG,
    filename='mybot.log',
    filemode='w')

from aiogram import Bot, Dispatcher, executor, types

from loader import dp, config

WEBHOOK_HOST = config.webhook_host
WEBHOOK_PATH = config.webhook_host
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

def old_vesion():
    ''' Version 1
        https://mastergroosha.github.io/telegram-tutorial-2/quickstart/
    '''
    import bot_messages as msgs
    import bot_commands as cmds

    mytoken=config.token
    bot = Bot(token=mytoken)

    dp = Dispatcher(bot)
    dp.register_message_handler(cmds.cmd_help, commands='help')
    dp.register_message_handler(cmds.cmd_start, commands='start')
    dp.register_message_handler(msgs.cmd_handler)

# Version 2
async def on_startup(dispatcher):
    ''' Run code after startup
    '''
    # await bot.set_webhook(WEBHOOK_URL)
    # await set_default_commands(dispatcher)
    # await set_default_messages(dispatcher)
    import bot_talk
    import handlers
    bot_talk.setup(dispatcher)
    handlers.setup(dispatcher)

''' on_shutdown(dispatcher)
    async def on_shutdown(dp):
        logging.warning('Shutting down..')
        # insert code here to run it before shutdown
        # Remove webhook (not acceptable in some cases)
        await bot.delete_webhook()
        # Close DB connection (if used)
        await dp.storage.close()
        await dp.storage.wait_closed()
'''

if __name__ == '__main__':
    from handlers.query_handler import dp
    from handlers.message_handler import dp
    # executor.start_polling(dp, skip_updates=True)   # V1
    executor.start_polling(dp, on_startup=on_startup) # V2

