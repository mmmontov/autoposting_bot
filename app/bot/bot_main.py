import asyncio
from aiogram import Bot, Dispatcher

from app.bot.handlers import admin_handlers, admin_callback_handlers # user_handlers, posts_handlers, , 
from app.bot.keyboards.main_menu import set_main_menu
from aiogram.fsm.storage.memory import MemoryStorage
# from app.services.database_management import BotDatabase
from app.bot.create_bot import bot # импорт объекта бота


async def start_bot():
    storage = MemoryStorage()
    
    dp: Dispatcher = Dispatcher(storage=storage)
    
    dp.include_router(admin_handlers.router)
    dp.include_router(admin_callback_handlers.router)

    await set_main_menu(bot)
    

    await bot.delete_webhook(drop_pending_updates=True)
    print('бот запустился')
    await dp.start_polling(bot, polling_timeout=20)
    


if __name__ == '__main__':
    asyncio.run(start_bot())

