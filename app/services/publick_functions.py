import asyncio

from app.bot.create_bot import bot
from app.services.queue_service import *
from datetime import datetime
from aiogram.exceptions import TelegramBadRequest
from pydantic import ValidationError
from aiogram.types import Message
from app.parsing.facts_parsing.facts_museum_parsing import gather_fact
from app.bot.keyboards.post_actions_keyboard import create_post_actions_kb
from app.parsing.recipes_parsing.ovkuse_parsing import create_recipe

SLEEP_TIMEOUT = 10

async def publick_post(channel: str):
    try:
        id, text, photo, video = await get_next_post_and_delete(channel=channel)
        if video:
            await bot.send_video(channel, caption=text, video=video)
        elif photo:
            await bot.send_photo(channel, caption=text, photo=photo)
        else:
            await bot.send_message(channel, text)
        print(f"[{datetime.now()}] {channel} пост отправлен в канал ")
    except TypeError:
        print('посты закончились')

# отправка сообщения с фактом
async def send_fact(message: Message, swap_post=True):
    try:
        post_text, image_url = await gather_fact()
        # если присутствует текст    
        if post_text:
            post_text += '\n\n@world_of_amazing_facts'
                
            await message.answer_photo(photo=image_url, 
                                    caption=post_text, 
                                    reply_markup=create_post_actions_kb(swap_post)) 
    except ValidationError as err:
        print('ошибка в отправке')
        await asyncio.sleep(SLEEP_TIMEOUT)
        await send_fact(message, swap_post)
    except TypeError as err:
        print('ошибка в распаковке')
        await asyncio.sleep(SLEEP_TIMEOUT)
        await send_fact(message, swap_post)
    except TelegramBadRequest:
        print('сообщение слишком длинное') 
        await asyncio.sleep(SLEEP_TIMEOUT)
        await send_fact(message, swap_post)
        
# отправка сообщения с рецептом
async def send_recipe(message: Message, swap_post=True):
    try:
        text, photo = await create_recipe()
        recipe_message = await message.answer_photo(photo=photo, caption=text, 
                                                    reply_markup=create_post_actions_kb(swap_post))
        return recipe_message
    except ValidationError as err:
        print(f'ошибка в отправке {err}')
        await asyncio.sleep(SLEEP_TIMEOUT)
        await send_recipe(message, swap_post)
    except TypeError as err:
        print(f'ошибка в распаковке {err}')
        await asyncio.sleep(SLEEP_TIMEOUT)
        await send_recipe(message, swap_post)
    except TelegramBadRequest:
        print('сообщение слишком длинное') 
        await asyncio.sleep(SLEEP_TIMEOUT)
        await send_recipe(message, swap_post)

