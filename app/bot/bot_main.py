import asyncio
from aiogram import Bot, Dispatcher

from app.bot.handlers import callback_handlers, comand_handlers, admin_callback_handlers 
from app.bot.keyboards.main_menu import set_main_menu
from aiogram.fsm.storage.memory import MemoryStorage
from app.bot.create_bot import bot # импорт объекта бота
from app.bot.middlewares.callback_middlewares import UserAccessMiddleware
from app.core.utils import ChannelsControl
from app.services.user_data import users_data


async def start_bot():
    storage = MemoryStorage()
    
    dp: Dispatcher = Dispatcher(storage=storage)
    
    dp.include_router(comand_handlers.router)
    dp.include_router(admin_callback_handlers.router)
    dp.include_router(callback_handlers.router)
    
    dp.callback_query.middleware(UserAccessMiddleware())
    dp.message.middleware(UserAccessMiddleware())


    await set_main_menu(bot)
    

    ChannelsControl.check_schedulers()
    users_data.start_watching()

    await bot.delete_webhook(drop_pending_updates=True)
    print('бот запустился')
    await dp.start_polling(bot, polling_timeout=20)
    


if __name__ == '__main__':
    asyncio.run(start_bot())

