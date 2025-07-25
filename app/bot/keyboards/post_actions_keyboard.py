from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.bot.lexicon.lexicon import *

def create_inline_kb(dict: dict, layout: list[int]=[]) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    items = iter(dict.items())

    # итерируемся по числам которые обозначают кол-во кнопок в ряду
    for width in layout:
        bttns = []
        for _ in range(width):
            try:
                cd, txt = next(items)
                bttns.append(InlineKeyboardButton(text=txt, callback_data=cd))
            except StopIteration: 
                pass
        kb_builder.row(*bttns, width=width)
    
    # оставшиеся добавляем по одной в ряд
    rest = list(items)
    if rest:
        kb_builder.row(*[InlineKeyboardButton(text=txt, callback_data=cd) 
                        for cd, txt in rest], width=1)
    return kb_builder.as_markup()

# ======================= main callbacks ======================================

def create_post_actions_kb(swap_post: bool=True) -> InlineKeyboardMarkup:
    menu = CALLBACK_RU['main_actions']
    base_menu = menu.copy()
    base_menu.pop('swap_post')
    if swap_post:
        base_menu.update({'swap_post': menu['swap_post']})
        
    return create_inline_kb(base_menu, [1, 2, 1, 1])


def create_edit_post_kb(regenerate_text: bool=False) -> InlineKeyboardMarkup:
    menu = CALLBACK_RU['edit_menu']
    base_menu = menu.copy()
    base_menu.pop('regenerate_text')
    if regenerate_text:
        base_menu.update({'regenerate_text': menu['regenerate_text']})
    
    return create_inline_kb(base_menu, [2, 2, 1])


def create_main_menu_kb(channel_swap: bool=True, swap_post: bool=True) -> InlineKeyboardMarkup:
    menu = CALLBACK_RU['main_menu']
    base_menu = dict(list(CALLBACK_RU['main_menu'].items())[:5])
    if channel_swap: base_menu.update({'bot_mode': menu['bot_mode']})
    if swap_post: base_menu.update({'swap_post': menu['swap_post']})
    
    return create_inline_kb(base_menu, [2, 2, 1, 1])    
    
    
def create_edit_autoposting_time_kb() -> InlineKeyboardMarkup:
    return create_inline_kb(CALLBACK_RU['edit_time_autoposting'], [2])

def back_to_autoposting_time_kb() -> InlineKeyboardMarkup:
    return create_inline_kb(CALLBACK_RU['back_to_autoposting'])

def create_back_to_main_menu_kb() -> InlineKeyboardMarkup:
    return create_inline_kb(CALLBACK_RU['back_to_main_menu'])

def create_back_to_main_menu_or_skip_kb() -> InlineKeyboardMarkup:
    return create_inline_kb(CALLBACK_RU['back_to_main_menu_or_skip'], [2])


def create_choose_content_type_kb() -> InlineKeyboardMarkup:
    return create_inline_kb(CALLBACK_RU['choose_content_type'], [1, 1, 1, 2])

def create_back_to_choose_content_type_kb() -> InlineKeyboardMarkup:
    return create_inline_kb(CALLBACK_RU['back_to_choose_content_type'], [1])

# =============================================================================


# ==================== on buttons click =======================================


def create_main_actions_add_to_queue(swap_post: bool=True) -> InlineKeyboardMarkup:
    menu: dict = CALLBACK_RU['on_buttons_click']['main_actions_add_to_queue']
    base_menu = menu.copy()
    base_menu.pop('swap_post')
    if swap_post:
        base_menu.update({'swap_post': menu['swap_post']})
        
    return create_inline_kb(base_menu, [1, 2, 1, 1])
    
# ==================== admins keyboards =======================================

def create_admin_menu_kb() -> InlineKeyboardMarkup:
    return create_inline_kb(ADMIN_CALLBACK['admin_menu'], [1, 1, 1])

def back_to_admin_menu_kb() -> InlineKeyboardMarkup:
    return create_inline_kb(ADMIN_CALLBACK['back_to_admin_menu'], [1])

def create_user_menu_kb() -> InlineKeyboardMarkup:
    return create_inline_kb(ADMIN_CALLBACK['user_menu'], [1, 2, 1])

def create_confirm_delete_user_kb(user_id) -> InlineKeyboardMarkup:
    user_id = str(user_id)
    data = replace_user('confirm_user_delete', user_id)
    return create_inline_kb(data, [2])

def create_back_to_user_menu_kb(user_id) -> InlineKeyboardMarkup:
    user_id = str(user_id)
    data = replace_user('back_to_user_menu', user_id)
    return create_inline_kb(data)

def create_channel_menu_kb(user_id) -> InlineKeyboardMarkup:
    user_id = str(user_id)
    data = replace_user('channel_menu', user_id)
    return create_inline_kb(data, [2, 1])

def create_confirm_delete_channel_kb(channel_id) -> InlineKeyboardMarkup:
    channel_id = str(channel_id)
    data = replace_user('confirm_channel_delete', channel_id=channel_id)
    return create_inline_kb(data, [2])



def replace_user(admin_index, user_id=None, channel_id=None):
    data = ADMIN_CALLBACK[admin_index].copy()
    new_data = {}
    for k, v in data.items():
        if user_id and k == 'user:':
            k = f'user:{user_id}'
        if channel_id and k == 'channel:':
            k = f'channel:{channel_id}'
        
        new_data[k] = v
    return new_data