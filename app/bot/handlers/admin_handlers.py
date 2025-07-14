import asyncio
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import Router

from app.bot.keyboards.post_actions_keyboard import *
from app.core.utils import ChannelsControl
from app.services.format_text import format_main_menu_text

router = Router()



# get bot menu (главное меню бота)
@router.message(Command(commands='bot_menu'))
async def get_bot_menu(message: Message):
    text = await format_main_menu_text(ChannelsControl.channels_autoposting[ChannelsControl.active_channel])
    await message.answer(text=text, 
                         reply_markup=create_main_menu_kb())