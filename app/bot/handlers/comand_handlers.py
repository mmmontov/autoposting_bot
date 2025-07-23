import asyncio
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import Router, F

from app.bot.keyboards.post_actions_keyboard import *
from app.services.format_text import format_main_menu_text
from app.services.user_data import users_data
from app.db.models.queue_registry import tables_registry
from app.core.utils import ChannelsControl
from app.core.config import config

router = Router()



# get bot menu (главное меню бота)
@router.message(Command(commands=('bot_menu', 'start')))
async def get_bot_menu(message: Message, can_swap_channel: bool, swap_post: bool):
    if str(message.from_user.id) not in users_data.get_all_user_ids():
        await message.answer('У вас нет доступа к боту.')
        return
    text = await format_main_menu_text(message.from_user.id)
    await message.answer(text=text, 
                         reply_markup=create_main_menu_kb(can_swap_channel, swap_post))
    
    
# get admin menu
@router.message(Command(commands='admin'), F.from_user.id.in_(list(map(int, config.tg_bot.admin_ids))))
async def get_admin_menu(message: Message):
    text = '🔧 Админ меню'
    await message.answer(text=text, 
                         reply_markup=create_admin_menu_kb())

    
