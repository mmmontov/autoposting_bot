import re
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, any_state, default_state
from aiogram.filters import StateFilter

from app.services.format_text import format_main_menu_text
from app.bot.keyboards.post_actions_keyboard import *
from app.core.config import config
from app.parsing.recipes_parsing.ovkuse_parsing import *
from app.core.utils import ChannelsControl
from app.services.queue_service import *
from app.services.scheduler import *

router = Router()


# ================================= FSM States ======================================
class AutopostingTimeSettings(StatesGroup):
    change_time = State()
    add_time = State()

# ================================= posts main menu =================================

# resend message_copy to my channel
@router.callback_query(F.data == 'publish_post')
async def process_publish_post(callback: CallbackQuery):
    new_message = await callback.message.delete_reply_markup()
    await new_message.send_copy(ChannelsControl.active_channel, reply_markup=None)
    # возвращаем клавиатуру действий
    await callback.message.edit_reply_markup(reply_markup=create_post_actions_kb())
    await callback.answer()
    

    
# set edit post inline buttons markup
@router.callback_query(F.data == 'edit_menu')
async def process_open_edit_menu(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=create_edit_post_kb())

# add post in database (queue)
@router.callback_query(F.data == 'add_to_queue')
async def process_add_to_queue(callback: CallbackQuery):
    photo_id = callback.message.photo[0].file_id
    post_text = callback.message.caption
    await add_post(ChannelsControl.active_channel, post_text, photo_id)
    await callback.message.edit_reply_markup(reply_markup=create_main_actions_add_to_queue())
    await callback.answer()
    
# get new post
@router.callback_query(F.data == 'swap_post')
async def process_swap_post(callback: CallbackQuery):
    await callback.message.delete()
    await ChannelsControl.parsers[ChannelsControl.active_channel](callback.message)


# ===================================================================================    
    
    
    
    
    
  
# ========================= edit post menu ==========================================   

# delete last paragraph in post
@router.callback_query(F.data == 'delete_last_string')
async def process_delete_last_string(callback: CallbackQuery):
    text = callback.message.caption
    if text:
        split_text = text.split('\n')
        new_text = '\n'.join(split_text[:-1])
        await callback.message.edit_caption(caption=new_text, reply_markup=create_edit_post_kb())
    else:
        await callback.answer()
        

# delete first paragraph in post
@router.callback_query(F.data == 'delete_first_string')
async def process_delete_first_string(callback: CallbackQuery):
    text = callback.message.caption
    if text:
        split_text = text.split('\n')
        new_text = split_text[0] + '\n'.join(split_text[2:])
        await callback.message.edit_caption(caption=new_text, reply_markup=create_edit_post_kb())
    else:
        await callback.answer()
        
# regenerate text in post (cpecially for recipes)
@router.callback_query(F.data == 'regenerate_text')
async def process_regenerate_text(callback: CallbackQuery):
    if ChannelsControl.active_channel == '@best_tasty_recipes':
        text = callback.message.caption
        new_text = await generate_recipe(text)
        await callback.message.edit_caption(caption=new_text,
                                            reply_markup=create_edit_post_kb())
        await callback.answer()
    else:
        await callback.answer(text='⚠️ эта функция недоступна для постов из этого канала',
                                show_alert=True)
        
       
# add link to my channel in post text
@router.callback_query(F.data == 'add_link')
async def process_add_link_to_my_channel(callback: CallbackQuery):
    new_text = callback.message.caption + f'\n\n{ChannelsControl.active_channel}'
    try:
        await callback.message.edit_caption(caption=new_text, reply_markup=create_edit_post_kb())
    except TelegramBadRequest:
        print('сообщение получается слишком длинным')
        await callback.answer()
        
# back to main_actions inline keyboard 
@router.callback_query(F.data == 'main_actions')
async def process_back_to_main_actions_menu(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=create_post_actions_kb())
    
# ====================================================================================   
    
    
    


# ============================ bot main menu ============================================


# back to main menu
@router.callback_query(F.data == 'main_menu')
async def process_main_menu(callback: CallbackQuery):
    await callback.message.delete()
    text = await format_main_menu_text(ChannelsControl.channels_autoposting[ChannelsControl.active_channel])
    await callback.message.answer(text=text, 
                         reply_markup=create_main_menu_kb())


# autoposting time settings
@router.callback_query(F.data == 'autoposting_time')
async def process_set_autoposting_time(callback: CallbackQuery, state: FSMContext):
    await state.set_state(default_state)
    autoposting_time = {
        f'{time}_time': time 
        for time in load_schedule(ChannelsControl.active_channel)
    }
    autoposting_time.update(CALLBACK_RU['autoposting_time_actions'])
    kb = create_inline_kb(autoposting_time, [2]*15)
    
    await callback.message.edit_text(
        text=f'Выберете время для редактирования или добавьте новое\nКанал {ChannelsControl.active_channel}',
        reply_markup=kb)


# publick last post in queue
@router.callback_query(F.data == 'last_post')
async def process_public_next_post_in_queue(callback: CallbackQuery):
    post = await get_last_post_and_delete(ChannelsControl.active_channel)
    if post:
        id, text, image = post
        await callback.message.answer_photo(image, text, reply_markup=create_post_actions_kb())
    await callback.answer()


# publick next post in queue
@router.callback_query(F.data == 'next_post')
async def process_public_next_post_in_queue(callback: CallbackQuery):
    post = await get_next_post_and_delete(ChannelsControl.active_channel)
    if post:
        id, text, image = post
        await callback.message.answer_photo(image, text, reply_markup=create_post_actions_kb())
    await callback.answer()


# start\stop queue auto-posting 
@router.callback_query(F.data == 'start_stop_queue')
async def process_start_stop_public_queue(callback: CallbackQuery):
    ChannelsControl.switch_autoposting()
    autoposting = ChannelsControl.channels_autoposting[ChannelsControl.active_channel]
    text = await format_main_menu_text(autoposting)

    await callback.message.edit_text(text, reply_markup=create_main_menu_kb())



# switch active channel
@router.callback_query(F.data.in_(config.tg_channel.channel_names))
async def process_switch_active_channel(callback: CallbackQuery):
    ChannelsControl.active_channel = callback.data 
    text = await format_main_menu_text(ChannelsControl.channels_autoposting[ChannelsControl.active_channel])
    await callback.message.edit_text(text=text,
                                     reply_markup=create_main_menu_kb())
    await callback.answer()


# open bot_mode menu
@router.callback_query(F.data == 'bot_mode')
async def process_open_bot_mode_menu(callback: CallbackQuery):
    await callback.message.edit_text(text='выбери канал для управления',
                                  reply_markup=create_bot_mode_menu())
    
    
    
# ====================================================================================   
    
    
    


# ========================= autoposting time settings =================================

# add new time
@router.callback_query(F.data.endswith('_time'))
async def process_edit_autoposting_time(callback: CallbackQuery, state: FSMContext):
    time = callback.data.split('_')[0]
    await state.set_state(AutopostingTimeSettings.change_time)
    await state.update_data(time=time)
    await callback.message.edit_text(text=f'{time}\nВведите новое время в формате\nЧАС:МИНУТЫ (14:30/05:15)',
                                     reply_markup=create_edit_autoposting_time_kb())
    
    
# delete autoposting time
@router.callback_query(F.data == 'delete_time_autoposting', StateFilter(AutopostingTimeSettings.change_time))
async def process_delete_autoposting_time(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    time = state_data['time']
    schedule: list = load_schedule(ChannelsControl.active_channel)
    del schedule[schedule.index(time)]
    schedule.sort()
    update_schedule(ChannelsControl.active_channel, schedule)
    
    await callback.message.edit_text(text='Время было удалено ✅',
                                     reply_markup=back_to_autoposting_time_kb())
    
    
# change autoposting time
@router.message(lambda x: re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', x.text) is not None, StateFilter(AutopostingTimeSettings.change_time))    
async def process_change_autoposting_time(message: Message, state: FSMContext):
    state_data = await state.get_data()
    time = state_data['time']
    schedule: list = load_schedule(ChannelsControl.active_channel)
    schedule[schedule.index(time)] = message.text
    schedule.sort()
    update_schedule(ChannelsControl.active_channel, schedule)
    await message.answer(text='Время было изменено ✅',
                                        reply_markup=back_to_autoposting_time_kb())

    
# add time
@router.callback_query(F.data == 'time_add')
async def process_time_add(callback: CallbackQuery, state: FSMContext):
    if len(load_schedule(ChannelsControl.active_channel)) < 8:
        await state.set_state(AutopostingTimeSettings.add_time)
        text = 'Введите время в формате\nЧАС:МИНУТЫ (14:30/05:15)'
    else:
        text = 'Нельзя добавить больше времён'
    
    await callback.message.edit_text(text=text,
                                     reply_markup=back_to_autoposting_time_kb())
    
# add time mesage
@router.message(lambda x: re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', x.text) is not None, StateFilter(AutopostingTimeSettings.add_time))
async def process_add_new_time(message: Message, state: FSMContext):
    schedule: list = load_schedule(ChannelsControl.active_channel)
    if message.text not in schedule:
        schedule.append(message.text)
        schedule.sort()
        update_schedule(ChannelsControl.active_channel, schedule)
        text = 'Время было добавлено ✅'
        await state.set_state(default_state)
    else:
        text = 'Такое время уже существует ❌'
    await message.answer(text=text,
                            reply_markup=back_to_autoposting_time_kb())
    
