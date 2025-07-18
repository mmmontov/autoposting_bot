from app.bot.create_bot import bot
from app.services.queue_service import *
from datetime import datetime
from aiogram.exceptions import TelegramBadRequest
from pydantic import ValidationError
from aiogram.types import Message
from app.parsing.facts_parsing.facts_museum_parsing import gather_fact
from app.bot.keyboards.post_actions_keyboard import create_post_actions_kb
from app.parsing.recipes_parsing.ovkuse_parsing import create_recipe

async def publick_post(channel: str):
    try:
        id, text, photo = await get_next_post_and_delete(channel=channel)
        await bot.send_photo(channel, caption=text, photo=photo)
        print(f"[{datetime.now()}] {channel} пост отправлен в канал ")
    except TypeError:
        print('посты закончились')


# отправка сообщения с фактом
async def send_fact(message: Message):
    try:
        post_text, image_url = await gather_fact()
        # если присутствует текст    
        if post_text:
            post_text += '\n\n@world_of_amazing_facts'
                
            await message.answer_photo(photo=image_url, 
                                    caption=post_text, 
                                    reply_markup=create_post_actions_kb()) 
    except ValidationError as err:
        print('ошибка в отправке')
        await send_fact(message)
    except TypeError as err:
        print('ошибка в распаковке')
        await send_fact(message)
    except TelegramBadRequest:
        print('сообщение слишком длинное') 
        await send_fact(message)
        
# отправка сообщения с рецептом
async def send_recipe(message: Message):
    try:
        text, photo = await create_recipe()
        recipe_message = await message.answer_photo(photo=photo, caption=text, 
                                                    reply_markup=create_post_actions_kb())
        return recipe_message
    except ValidationError as err:
        print(f'ошибка в отправке {err}')
        await send_recipe(message)
    except TypeError as err:
        print(f'ошибка в распаковке {err}')
        await send_recipe(message)
    except TelegramBadRequest:
        print('сообщение слишком длинное') 
        await send_recipe(message)

