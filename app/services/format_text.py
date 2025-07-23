from app.services.queue_service import get_queue
from app.services.user_data import users_data


# =============== formating texts in posts ===================================

async def format_main_menu_text(user_id: int):
    active_channel = users_data.get_active_channel(user_id)
    post_mode = users_data.get_autoposting(user_id, active_channel)
    queue_posts_count = len(await get_queue(active_channel))
    posting = 'включен 👍' if post_mode else 'выключен 👎'
    
    text = f'''актинвый канал - {active_channel}\n
автопостинг - <b>{posting}</b>\n
постов в очереди - <b>{queue_posts_count}</b>'''
    return text

# 👍👎


