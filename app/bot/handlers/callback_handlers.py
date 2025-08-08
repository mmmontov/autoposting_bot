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
from app.parsing.facts_parsing.facts_museum_parsing import generate_fact
from app.core.utils import ChannelsControl
from app.services.queue_service import *
from app.services.scheduler import *
from app.services.user_data import users_data
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()


# ================================= FSM States ======================================
class AutopostingTimeSettings(StatesGroup):
    change_time = State()
    add_time = State()


class CreatePostStates(StatesGroup):
    waiting_for_text_input = State()
    waiting_for_video_input = State()
    waiting_for_photo_input = State()
    waiting_for_content_type = State()


# ================================= posts main menu =================================

# resend message_copy to my channel
@router.callback_query(F.data == 'publish_post')
async def process_publish_post(callback: CallbackQuery, swap_post: bool):
    new_message = await callback.message.delete_reply_markup()
    await new_message.send_copy(users_data.get_active_channel(callback.from_user.id), reply_markup=None)
    # возвращаем клавиатуру действий
    await callback.message.edit_reply_markup(reply_markup=create_post_actions_kb(swap_post))
    await callback.answer()
    

    
# set edit post inline buttons markup
@router.callback_query(F.data == 'edit_menu')
async def process_open_edit_menu(callback: CallbackQuery, regenerate_post: bool):
    await callback.message.edit_reply_markup(reply_markup=create_edit_post_kb(regenerate_post))

# add post in database (queue)
@router.callback_query(F.data == 'add_to_queue')
async def process_add_to_queue(callback: CallbackQuery, swap_post: bool):
    photo_id = None
    video_id = None
    if callback.message.video:
        video_id = callback.message.video.file_id
        post_text = callback.message.caption
    elif callback.message.photo:
        photo_id = callback.message.photo[0].file_id
        post_text = callback.message.caption
    else:
        post_text = callback.message.text
    await add_post(users_data.get_active_channel(callback.from_user.id), post_text, photo_id, video_id)
    await callback.message.edit_reply_markup(reply_markup=create_main_actions_add_to_queue(swap_post))
    await callback.answer()
    
# get new post 
@router.callback_query(F.data == 'swap_post')
async def process_swap_post(callback: CallbackQuery, swap_post: bool):
    await callback.message.delete()
    await ChannelsControl.parsers[users_data.get_active_channel(callback.from_user.id)](callback.message, swap_post)


# ===================================================================================    
    
    
    
    
    
  
# ========================= edit post menu ==========================================   

# delete last paragraph in post
@router.callback_query(F.data == 'delete_last_string')
async def process_delete_last_string(callback: CallbackQuery, regenerate_post: bool):
    caption = callback.message.caption 
    post_text = callback.message.text
    text = caption if caption else post_text
    if text:
        split_text = text.split('\n')
        new_text = '\n'.join(split_text[:-1])
        if caption:
            await callback.message.edit_caption(caption=new_text, reply_markup=create_edit_post_kb(regenerate_post))
        elif post_text and new_text:
            await callback.message.edit_text(text=new_text, reply_markup=create_edit_post_kb(regenerate_post))
    else:
        await callback.answer()
        

# delete first paragraph in post
@router.callback_query(F.data == 'delete_first_string')
async def process_delete_first_string(callback: CallbackQuery, regenerate_post: bool):
    caption = callback.message.caption 
    post_text = callback.message.text
    text = caption if caption else post_text

    if text:
        split_text = text.split('\n')
        new_text = '\n'.join(split_text[1:])
        if caption:
            await callback.message.edit_caption(caption=new_text, reply_markup=create_edit_post_kb(regenerate_post))
        elif post_text and new_text:
            await callback.message.edit_text(text=new_text, reply_markup=create_edit_post_kb(regenerate_post))
    else:
        await callback.answer()
        
# regenerate text in post (cpecially for recipes) # переделать, удалить для всех, оставить только для себя
@router.callback_query(F.data == 'regenerate_text')
async def process_regenerate_text(callback: CallbackQuery, regenerate_post: bool):
    active_channel = users_data.get_active_channel(callback.from_user.id)
    text = callback.message.caption
    if active_channel == '@best_tasty_recipes':
        new_text = await generate_recipe(text)
        await callback.message.edit_caption(caption=new_text,
                                            reply_markup=create_edit_post_kb(regenerate_post))

    elif active_channel == '@factzap':
        new_text = await generate_fact(text)
        await callback.message.edit_caption(caption=new_text,
                                            reply_markup=create_edit_post_kb(regenerate_post))

    else:
        await callback.answer(text='⚠️ эта функция недоступна для постов из этого канала',
                                show_alert=True)
        
       
# add link to my channel in post text
@router.callback_query(F.data == 'add_link')
async def process_add_link_to_my_channel(callback: CallbackQuery, regenerate_post: bool):
    link = f'\n\n{users_data.get_active_channel(callback.from_user.id)}'
    try:
        if callback.message.caption:
            new_text = callback.message.caption + link
            await callback.message.edit_caption(caption=new_text, reply_markup=create_edit_post_kb(regenerate_post))
        elif callback.message.text:
            new_text = callback.message.text + link
            await callback.message.edit_text(text=new_text, reply_markup=create_edit_post_kb(regenerate_post))
        else: 
            await callback.message.edit_caption(caption=link, reply_markup=create_edit_post_kb(regenerate_post))
    except TelegramBadRequest:
        print('сообщение получается слишком длинным')
        await callback.answer()
        
# back to main_actions inline keyboard 
@router.callback_query(F.data == 'main_actions')
async def process_back_to_main_actions_menu(callback: CallbackQuery, swap_post: bool):
    await callback.message.edit_reply_markup(reply_markup=create_post_actions_kb(swap_post))
    
# ====================================================================================   
    
    
    


# ============================ bot main menu ============================================


# back to main menu
@router.callback_query(F.data == 'main_menu')
async def process_main_menu(callback: CallbackQuery, can_swap_channel: bool, swap_post: bool):
    await callback.message.delete()
    text = await format_main_menu_text(callback.from_user.id)
    await callback.message.answer(text=text, 
                         reply_markup=create_main_menu_kb(can_swap_channel, swap_post))


# autoposting time settings
@router.callback_query(F.data == 'autoposting_time')
async def process_set_autoposting_time(callback: CallbackQuery, state: FSMContext):
    active_channel = users_data.get_active_channel(callback.from_user.id)
    active_channel = users_data.get_active_channel(callback.from_user.id)
    schedule: list = users_data.get_schedule(callback.from_user.id, active_channel)
    await state.set_state(default_state)
    autoposting_time = {
        f'{time}_time': time 
        for time in schedule
    }
    autoposting_time.update(CALLBACK_RU['autoposting_time_actions'])
    kb = create_inline_kb(autoposting_time, [2]*15)
    
    await callback.message.edit_text(
        text=f'Выберете время для редактирования или добавьте новое\nКанал {active_channel}',
        reply_markup=kb)


# get last post in queue
@router.callback_query(F.data == 'last_post')
async def process_public_next_post_in_queue(callback: CallbackQuery, swap_post: bool):
    post = await get_last_post_and_delete(users_data.get_active_channel(callback.from_user.id))
    if post:
        id, text, image, video = post
        if video:
            await callback.message.answer_video(video=video, caption=text, reply_markup=create_post_actions_kb(swap_post))
        elif image:
            await callback.message.answer_photo(photo=image, caption=text, reply_markup=create_post_actions_kb(swap_post))
        else:
            await callback.message.answer(text=text, reply_markup=create_post_actions_kb(swap_post))
    await callback.answer()


# get next post in queue
@router.callback_query(F.data == 'next_post')
async def process_public_next_post_in_queue(callback: CallbackQuery, swap_post: bool):
    post = await get_next_post_and_delete(users_data.get_active_channel(callback.from_user.id))
    if post:
        id, text, image, video = post
        if video:
            await callback.message.answer_video(video=video, caption=text, reply_markup=create_post_actions_kb(swap_post))
        elif image:
            await callback.message.answer_photo(photo=image, caption=text, reply_markup=create_post_actions_kb(swap_post))
        else:
            await callback.message.answer(text=text, reply_markup=create_post_actions_kb(swap_post))
    await callback.answer()


# start\stop queue auto-posting 
@router.callback_query(F.data == 'start_stop_queue')
async def process_start_stop_public_queue(callback: CallbackQuery, can_swap_channel: bool, swap_post: bool):
    active_channel = users_data.get_active_channel(callback.from_user.id)
    autoposting = users_data.get_autoposting(callback.from_user.id, active_channel)
    switch_autoposting = await users_data.set_autoposting(callback.from_user.id, active_channel, not autoposting)
    if switch_autoposting: 
        if autoposting: ChannelsControl.schedulers[active_channel].stop() 
        else: ChannelsControl.schedulers[active_channel].start()
    text = await format_main_menu_text(callback.from_user.id)

    await callback.message.edit_text(text, reply_markup=create_main_menu_kb(can_swap_channel, swap_post))



# switch active channel
@router.callback_query(lambda x: x.data in users_data.get_user_channels(x.from_user.id))
async def process_switch_active_channel(callback: CallbackQuery, can_swap_channel: bool):
    await users_data.set_active_channel(callback.from_user.id, callback.data)
    swap_post = ChannelsControl.get_swap_post_status(callback.from_user.id)
    text = await format_main_menu_text(callback.from_user.id) 
    await callback.message.edit_text(text=text,
                                     reply_markup=create_main_menu_kb(can_swap_channel, swap_post))
    await callback.answer()


# open bot_mode menu
@router.callback_query(F.data == 'bot_mode')
async def process_open_bot_mode_menu(callback: CallbackQuery):
    keyboard = create_inline_kb({link: link for link in users_data.get_user_channels(callback.from_user.id)})
    # print(list(users_data.get_all_schedules().keys()))
    await callback.message.edit_text(text='выбери канал для управления',
                                  reply_markup=keyboard)
    
    
    
# ====================================================================================   
    
# ========================= create new post ==========================================
    

# start create post process
@router.callback_query(F.data == 'create_post')
async def process_start_create_post(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(CreatePostStates.waiting_for_content_type)
    kb = create_choose_content_type_kb()
    await callback.message.edit_text(
        text="Что вы хотите добавить в пост?",
        reply_markup=kb
    )
    await callback.answer()

# Обработка выбора типа контента
@router.callback_query(F.data.in_(['add_text', 'add_photo', 'add_video']), StateFilter(CreatePostStates.waiting_for_content_type))
async def process_content_type_choice(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'add_text':
        await state.set_state(CreatePostStates.waiting_for_text_input)
        await callback.message.edit_text(
            text="Введите текст для поста:",
            reply_markup=create_back_to_choose_content_type_kb()
        )
    elif callback.data == 'add_photo':
        await state.set_state(CreatePostStates.waiting_for_photo_input)
        await callback.message.edit_text(
            text="Отправьте фотографию для поста:",
            reply_markup=create_back_to_choose_content_type_kb()
        )
    elif callback.data == 'add_video':
        await state.set_state(CreatePostStates.waiting_for_video_input)
        await callback.message.edit_text(
            text="Отправьте видео для поста:",
            reply_markup=create_back_to_choose_content_type_kb()
        )
    await callback.answer()

# Получение текста
@router.message(StateFilter(CreatePostStates.waiting_for_text_input))
async def process_receive_post_text(message: Message, state: FSMContext):
    await state.update_data(post_text=message.text)
    kb = create_choose_content_type_kb()
    await state.set_state(CreatePostStates.waiting_for_content_type)
    await message.answer(
        text="Добавить ещё что-то?",
        reply_markup=kb
    )

# Получение фото
@router.message(F.photo, StateFilter(CreatePostStates.waiting_for_photo_input))
async def process_receive_post_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)
    kb = create_choose_content_type_kb()
    await state.set_state(CreatePostStates.waiting_for_content_type)
    await message.answer(
        text="Добавить ещё что-то?",
        reply_markup=kb
    )

# Получение видео
@router.message(F.video, StateFilter(CreatePostStates.waiting_for_video_input))
async def process_receive_post_video(message: Message, state: FSMContext):
    video_id = message.video.file_id
    await state.update_data(video_id=video_id)
    kb = create_choose_content_type_kb()
    await state.set_state(CreatePostStates.waiting_for_content_type)
    await message.answer(
        text="Добавить ещё что-то?",
        reply_markup=kb
    )

# Кнопка "Готово" для подтверждения поста
@router.callback_query(F.data == 'done', StateFilter(CreatePostStates.waiting_for_content_type))
async def process_confirm_post(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    post_text = data.get("post_text", "")
    photo_id = data.get("photo_id")
    video_id = data.get("video_id")
    await callback.message.delete()
    if video_id:
        await callback.message.answer_video(
            video=video_id,
            caption=post_text,
            reply_markup=create_post_actions_kb(swap_post=False)
        )
        if photo_id:
            await callback.answer(text='⚠️ Пост содержит и фото и видео. Будет отправлено только видео',
                                  show_alert=True)
        
    elif photo_id:
        await callback.message.answer_photo(
            photo=photo_id,
            caption=post_text,
            reply_markup=create_post_actions_kb(swap_post=False)
        )
    elif post_text:
        await callback.message.answer(
            text=post_text,
            reply_markup=create_post_actions_kb(swap_post=False)
        )
    else:
        await callback.answer(
            text="Пост не содержит контента. Пожалуйста, добавьте текст, фото или видео.",
            show_alert=True
        )
    await state.clear()

    
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
    active_channel = users_data.get_active_channel(callback.from_user.id)
    schedule: list = users_data.get_schedule(callback.from_user.id, active_channel)
    del schedule[schedule.index(time)]
    schedule.sort()
    await users_data.set_schedule(callback.from_user.id, active_channel, schedule)
    
    await callback.message.edit_text(text='Время было удалено ✅',
                                     reply_markup=back_to_autoposting_time_kb())
    
    
# change autoposting time
@router.message(lambda x: re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', x.text) is not None, StateFilter(AutopostingTimeSettings.change_time))    
async def process_change_autoposting_time(message: Message, state: FSMContext):
    state_data = await state.get_data()
    time = state_data['time']
    active_channel = users_data.get_active_channel(message.from_user.id)
    schedule: list = users_data.get_schedule(message.from_user.id, active_channel)
    schedule[schedule.index(time)] = message.text
    schedule.sort()
    await users_data.set_schedule(message.from_user.id, active_channel, schedule)
    await message.answer(text='Время было изменено ✅',
                                        reply_markup=back_to_autoposting_time_kb())

    
# add time
@router.callback_query(F.data == 'time_add')
async def process_time_add(callback: CallbackQuery, state: FSMContext):
    active_channel = users_data.get_active_channel(callback.from_user.id)
    if len(users_data.get_schedule(callback.from_user.id, active_channel)) < 8:
        await state.set_state(AutopostingTimeSettings.add_time)
        text = 'Введите время в формате\nЧАС:МИНУТЫ (14:30/05:15)'
    else:
        text = 'Нельзя добавить больше времён'
    
    await callback.message.edit_text(text=text,
                                     reply_markup=back_to_autoposting_time_kb())
    
# add time mesage
@router.message(lambda x: re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', x.text) is not None, StateFilter(AutopostingTimeSettings.add_time))
async def process_add_new_time(message: Message, state: FSMContext):
    active_channel = users_data.get_active_channel(message.from_user.id)
    schedule: list = users_data.get_schedule(message.from_user.id, active_channel)
    if message.text not in schedule:
        schedule.append(message.text)
        schedule.sort()
        await users_data.set_schedule(message.from_user.id, active_channel, schedule)
        text = 'Время было добавлено ✅'
        await state.set_state(default_state)
    else:
        text = 'Такое время уже существует ❌'
    await message.answer(text=text,
                            reply_markup=back_to_autoposting_time_kb())
    
