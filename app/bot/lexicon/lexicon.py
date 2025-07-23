
LEXICON_RU = {
    '/start': 'приветик'
}

CALLBACK_RU: dict[str, dict[str, str | dict]] = {
    'main_actions': {
        'publish_post': '✅ опубликовать пост',
        'edit_menu': '✏️ редактировать пост',
        'add_to_queue': '📆 добавить в очередь',
        'swap_post': '🔄 другой пост',
        'main_menu': '🏠 Главное меню',
    },
    'edit_menu': {
        'delete_first_string': '🔼🗑 удалить первый абзац',
        'delete_last_string': '🔽🗑 удалить последний абзац',
        'regenerate_text': '⚙️ перегенерировать текст',
        'add_link': '✉️ добавить ссылку на себя',
        'main_actions': '⬅️ назад'
    },
    'main_menu': {
        'start_stop_queue': '⏯ вкл/выкл автопубликацию очереди',
        'autoposting_time': '⏰ время автопубликации',
        'next_post': '⏩ получить следующий пост',
        'last_post': '⏪ получить последний пост',
        'create_post': '🖋️ Создать пост', 
        'bot_mode': '🔁 переключение каналов',
        'swap_post': '➡️ получить пост'
    },
    'autoposting_time_actions': {
        'time_add': '➕ Добавить время',
        'main_menu': '⬅️ назад'
    },
    
    'edit_time_autoposting': {
        'autoposting_time': '⬅️ назад',
        'delete_time_autoposting': '🗑 удалить время'
    },
    'back_to_autoposting': {
        'autoposting_time': '⬅️ назад'
    },
    'back_to_main_menu': {
        'main_menu': '⬅️ назад'
    },
    'back_to_main_menu_or_skip': {
        'main_menu': '⬅️ назад', 
        'skip': '⏩ пропустить'
    },
    
    'on_buttons_click': {
        'main_actions_add_to_queue':
            {
                'publish_post': '✅ опубликовать пост',
                'edit_menu': '✏️ редактировать пост',
                'none': '📝 добавлено в очередь',
                'swap_post': '🔄 другой пост',
                'main_menu': '🏠 Главное меню',
            },
    }
}

ADMIN_CALLBACK: dict[str, dict[str, str | dict]] = {
    'admin_menu': {
        'add_user': '➕ добавить пользователя',
        'all_users': '🧑‍💻 все пользователи',
        'update_users': '🔄 обновить базу пользователей'
    },
    'back_to_admin_menu': {
        'admin_menu': '⬅️ назад'
    },
    'user_menu': {
        'user_channels': '💼 каналы пользователя',
        'change_username': '✏️ изменить имя пользователя',
        'delete_user': '🗑 удалить пользователя',
        'all_users': '⬅️ назад'
    },
    'confirm_user_delete': {
        'user:': '❌ Отмена',
        'confirm_delete_user': '✅ Удалить'
    },
    'user_channels': {
        'user:': '⬅️ назад',
        'add_chanel': '➕ добавить канал'
    },
    'back_to_user_menu': {
        'user:': '⬅️ назад'
    },
    'channel_menu': {
        'delete_channel': '🗑 удалить канал',
        'switch_parsing_status': '⚙️ изменить статус parsing',
        'user_channels': '⬅️ назад'
    },
    'confirm_channel_delete': {
        'channel:': '❌ Отмена',
        'confirm_delete_channel': '✅ Удалить'
    }
    
}

LEXICON_COMMANDS = {
    '/bot_menu': 'меню бота'
}


# ✅❌🔄✏️📆🗑🔼🔽⬅️✉️⏪⏩⏯🔁➡️📝
# 🏠⚙️⏰➕🖋️🧑‍💻🔧💼👍👎⛔