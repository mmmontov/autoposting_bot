from app.core.config import config

LEXICON_RU = {
    '/start': 'приветик'
}

CALLBACK_RU: dict[str, dict] = {
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
        'bot_mode': '🔁 переключение каналов',
        'swap_post': '➡️ получить пост'
    },
    'bot_mode': {
        link: link for link in config.tg_channel.channel_names
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

LEXICON_COMMANDS = {
    '/bot_menu': 'меню бота'
}


# ✅❌🔄✏️📆🗑🔼🔽⬅️✉️⏪⏩⏯🔁➡️📝🏠⚙️⏰➕