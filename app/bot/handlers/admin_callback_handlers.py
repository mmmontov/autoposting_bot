from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, any_state, default_state
from aiogram.filters import StateFilter
from datetime import datetime

from app.services.format_text import format_main_menu_text
from app.bot.keyboards.post_actions_keyboard import *
from app.core.config import config
from app.parsing.recipes_parsing.ovkuse_parsing import *
from app.core.utils import ChannelsControl, update_system
from app.services.queue_service import *
from app.services.scheduler import *
from app.services.user_data import users_data
from app.bot.middlewares.admin_middlewares import AdminOnlyMiddleware


router = Router()
router.callback_query.middleware(AdminOnlyMiddleware())
router.message.middleware(AdminOnlyMiddleware())

# ================================= FSM States ======================================

class AddUserFSM(StatesGroup):
    waiting_for_userid = State()
    waiting_for_username = State()
    waiting_for_channel = State()
    

class UserProfileFSM(StatesGroup):
    user_profile = State()
    delete_user = State()
    waiting_for_username = State()
    waiting_for_channel = State()
    

# ===================================================================================

@router.callback_query(F.data == 'admin_menu')
async def process_admin_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    text = '🔧 Админ меню'
    await callback.message.edit_text(text=text, 
                                     reply_markup=create_admin_menu_kb())
    await callback.answer()



@router.callback_query(F.data == 'update_users')
async def process_update_users(callback: CallbackQuery):
    await update_system()
    await callback.answer('Информация о пользователях обновлена.', show_alert=True)
    

# ========================== Add user with channel =================================

# добавление нового пользователя 
@router.callback_query(F.data == 'add_user')
async def process_add_user(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddUserFSM.waiting_for_userid)
    await callback.message.edit_text(text='введите id пользователя например (5689551653)',
                                     reply_markup=back_to_admin_menu_kb())
    
# ввод userid
@router.message(StateFilter(AddUserFSM.waiting_for_userid))
async def process_userid_input(message: Message, state: FSMContext):
    user_id = message.text.strip()
    if not user_id.isdigit():
        await message.answer('ID пользователя должен быть числом. Попробуйте еще раз.')
        return
    
    await state.update_data(user_id=user_id)
    await state.set_state(AddUserFSM.waiting_for_username)
    await message.answer('Введите имя пользователя',
                         reply_markup=back_to_admin_menu_kb())
    
# ввод имени пользователя 
@router.message(StateFilter(AddUserFSM.waiting_for_username))
async def process_username_input(message: Message, state: FSMContext):
    username = message.text.strip()
    if not username:
        await message.answer('Имя пользователя не может быть пустым. Попробуйте еще раз.')
        return
    
    await state.update_data(username=username)
    await state.set_state(AddUserFSM.waiting_for_channel)
    await message.answer('Введите ID канала пользователя (например, @test_channel)',
                         reply_markup=back_to_admin_menu_kb())
    
# ввод канала пользователя
@router.message(StateFilter(AddUserFSM.waiting_for_channel))
async def process_channel_input(message: Message, state: FSMContext):
    channel_id = message.text.strip()
    if not channel_id or not channel_id.startswith('@'):
        await message.answer('ID канала не может быть пустым и должен начинаться с @. Попробуйте еще раз.')
        return
    
    data = await state.get_data()
    user_id = data.get('user_id')
    username = data.get('username')
    
    try:
        await users_data.add_user_channel(user_id, channel_id, username)
        await message.answer(f'Пользователь "{username}" с ID {user_id} и каналом {channel_id} успешно добавлен.',
                             reply_markup=back_to_admin_menu_kb())
    except Exception as e:
        await message.answer(f'Ошибка при добавлении пользователя: {str(e)}',
                             reply_markup=back_to_admin_menu_kb())
        
    await update_system()
    
    await state.clear()
    
    
# ==================================================================================



# ========================== edit all users ========================================

# получение всех пользователей
@router.callback_query(F.data == 'all_users')
async def process_all_users(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    users = users_data.get_all_user_ids()
    if not users:
        await callback.answer('Нет пользователей для редактирования.', show_alert=True)
        return
    
    text = '📋 Все пользователи:\n\n'
    data = {f'user:{user_id}': users_data.get_user_name(user_id)
            for user_id in users}
    data.update(ADMIN_CALLBACK['back_to_admin_menu'])

    await callback.message.edit_text(text=text, reply_markup=create_inline_kb(data, [2]*50))
    await callback.answer()
    
    
# профиль пользователя
@router.callback_query(F.data.startswith('user:'))
async def process_user_menu(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserProfileFSM.user_profile)
    user_id = callback.data.split(':')[1].strip()
    username = users_data.get_user_name(user_id)
    await state.update_data(user_id=user_id)
    await state.update_data(username=username)
    await callback.message.edit_text(text=f'Редактирование пользователя: {username} ({user_id})',
                                     reply_markup=create_user_menu_kb())
    
    
# подтверждение удаления пользователя
@router.callback_query(F.data == 'delete_user')
async def process_user_delete(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('user_id')
    await state.set_state(UserProfileFSM.delete_user)
    await callback.message.edit_text(text='Вы уверены, что хотите удалить пользователя?',
                                     reply_markup=create_confirm_delete_user_kb(user_id))
    
# удаление пользователя
@router.callback_query(F.data == 'confirm_delete_user', StateFilter(UserProfileFSM.delete_user))
async def process_confirm_delete_user(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('user_id')
    await users_data.delete_user(user_id)
    await callback.message.edit_text(text='✅ Пользователь был удалён',
                                     reply_markup=back_to_admin_menu_kb())


# все каналы пользователя
@router.callback_query(F.data == 'user_channels')
async def process_all_user_channels(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    username = data.get('username')
    user_id = data.get('user_id')
    user_channels = users_data.get_user_channels(user_id=user_id)
    channels_callback = {f'cahnnel:{channel}': channel for channel in user_channels}
    channels_callback.update(replace_user('user_channels', user_id))
    
    await callback.message.edit_text(text=f'каналы пользователя: "{username}" ({user_id})',
                                     reply_markup=create_inline_kb(channels_callback, [1]*len(user_channels)+[2]))
    


# добавление канала пользователю
@router.callback_query(F.data == 'add_chanel')
async def process_add_user_channel(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('user_id')
    user_channels = users_data.get_user_channels(user_id)  
    if len(user_channels) < 8:
        await state.set_state(UserProfileFSM.waiting_for_channel)
        await callback.message.edit_text(text='Введите ID канала пользователя\n(например, @test_channel)',
                                        reply_markup=create_back_to_user_menu_kb(user_id))
    else:
        await callback.answer('Максимальное количество каналов пользователя достигнуто.', 
                              show_alert=True)
    
# ввод канала пользователя
@router.message(StateFilter(UserProfileFSM.waiting_for_channel))
async def process_user_channel_input(message: Message, state: FSMContext):
    channel_id = message.text.strip()
    if not channel_id or not channel_id.startswith('@'):
        await message.answer('ID канала не может быть пустым и должен начинаться с @. Попробуйте еще раз.')
        return
    
    data = await state.get_data()
    user_id = data.get('user_id')
    
    try:
        await users_data.add_user_channel(user_id, channel_id)
        await message.answer(f'Канал {channel_id} успешно добавлен пользователю {user_id}.',
                             reply_markup=create_back_to_user_menu_kb(user_id))
        await update_system()
    except Exception as e:
        await message.answer(f'Ошибка при добавлении канала: {str(e)}',
                             reply_markup=create_back_to_user_menu_kb(user_id))
    
    
# меню канала пользователя
@router.callback_query(F.data.startswith('cahnnel:'))
async def process_channel_menu(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('user_id')
    channel_name = callback.data.split(':')[1]
    await state.update_data(channel_name=channel_name)
    await callback.message.edit_text(text=f'Канал: {channel_name}',
                                     reply_markup=create_channel_menu_kb(user_id))
    
    
# изменить статус parsing канала
@router.callback_query(F.data == 'switch_parsing_status')
async def process_switch_parsing_status(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('user_id')
    channel_name = data.get('channel_name')
    current_status = users_data.get_parsing(user_id, channel_name)
    new_status = not current_status
    await users_data.set_parsing(user_id, channel_name, new_status)
    await callback.answer(text=f'Статус парсинга канала {channel_name} {"включён 👍" if new_status else "выключён 👎"}',
                                     show_alert=True)
    await update_system()
    
# удалить канал пользователя (дальше будет подтверждение)
@router.callback_query(F.data == 'delete_channel')
async def process_delete_channel(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    channel_name = data.get('channel_name')
    user_id = data.get('user_id')
    user_channels = users_data.get_user_channels(user_id)
    if len(user_channels) == 1:
        await callback.answer('⛔ Нельзя удалить последний канал пользователя.', show_alert=True)
        return
    await callback.message.edit_text(text=f'Вы уверены, что хотите удалить канал {channel_name}?',
                                     reply_markup=create_confirm_delete_channel_kb(channel_name))
    
# подтверждение удаления канала
@router.callback_query(F.data == 'confirm_delete_channel')
async def process_confirm_delete_channel(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('user_id')
    channel_name = data.get('channel_name')
    
    try:
        await users_data.delete_user_channel(user_id, channel_name)
        await callback.message.edit_text(text=f'Канал {channel_name} был удалён.',
                                         reply_markup=create_back_to_user_menu_kb(user_id))
        await update_system()
    except Exception as e:
        await callback.message.edit_text(text=f'Ошибка при удалении канала: {str(e)}',
                                         reply_markup=create_back_to_user_menu_kb(user_id))
        
        
# изменение имени пользователя
@router.callback_query(F.data == 'change_username')
async def process_change_username(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('user_id')
    await state.set_state(UserProfileFSM.waiting_for_username)
    await callback.message.edit_text(text='✏️ Введите новое имя пользователя',
                                     reply_markup=create_back_to_user_menu_kb(user_id))
    
# ввод нового имени пользователя
@router.message(StateFilter(UserProfileFSM.waiting_for_username))
async def process_waiting_for_username(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('user_id')
    new_username = message.text
    await users_data.set_user_name(user_id, new_username)
    await message.answer(text=f'✅ Имя пользователя изменено на {new_username}',
                         reply_markup=create_back_to_user_menu_kb(user_id))
    await state.clear()