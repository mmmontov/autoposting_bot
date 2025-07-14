from app.core.utils import ChannelsControl
from app.services.queue_service import get_queue


# =============== formating texts in posts ===================================

async def format_main_menu_text(post_mode):
    # db = BotDatabase(config.database.path)
    queue_posts_count = len(await get_queue(ChannelsControl.active_channel))
    posting = 'включен 👍' if post_mode else 'выключен 👎'
    
    text = f'''актинвый канал - {ChannelsControl.active_channel}\n
автопостинг - <b>{posting}</b>\n
постов в очереди - <b>{queue_posts_count}</b>'''
    return text

# 👍👎


