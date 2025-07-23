from pathlib import Path
from app.services.scheduler import DynamicScheduler
from datetime import datetime

from app.core.config import config
from app.services.publick_functions import publick_post, send_recipe, send_fact
from app.services.user_data import users_data
from app.services.db_initializer import init_channels_tables
from app.db.models.queue_registry import tables_registry
  
class ChannelsControl:
    parsers = {
        '@best_tasty_recipes': send_recipe,
        '@world_of_amazing_facts': send_fact
    }
    
    regenerate_post_accept = [
        '@best_tasty_recipes'
    ]
    
    
    schedulers = {
        name: DynamicScheduler(name, 
                               Path(config.database.users_path), 
                               publick_post) 
        for name in list(users_data.get_all_schedules().keys())
    }
    
    @classmethod
    def update_schedulers(cls):
        current_schedules = set(users_data.get_all_schedules().keys())
        existing_schedulers = set(cls.schedulers.keys())

        # Add new schedulers
        for name in current_schedules - existing_schedulers:
            cls.schedulers[name] = DynamicScheduler(
                name,
                Path(config.database.users_path),
                publick_post
            )

        # Remove schedulers that no longer exist
        for name in existing_schedulers - current_schedules:
            scheduler = cls.schedulers.pop(name)
            scheduler.stop()
    
    @classmethod
    def check_schedulers(cls):
        for name, scheduler in list(cls.schedulers.items()):
            if users_data.get_channels_autoposting()[name]:
                scheduler.start()
                print(f"[{datetime.now()}] {name} был снова запущен")

    @classmethod
    def get_swap_post_status(cls, id):
        active_channel = users_data.get_active_channel(id)
        return active_channel in cls.parsers and users_data.get_parsing(id, active_channel)
    
    @classmethod
    def get_regenerate_post_status(cls, id):
        active_channel = users_data.get_active_channel(id)
        return users_data.get_active_channel(id) in cls.regenerate_post_accept and users_data.get_parsing(id, active_channel)
    
    @classmethod
    def get_can_channel_swap(cls, id):
        return len(users_data.get_user_channels(id)) > 1
    
    
    
async def update_system():
    tables_registry.update_queue_tables()
    await init_channels_tables()
    ChannelsControl.update_schedulers()