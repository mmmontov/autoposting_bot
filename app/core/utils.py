from pathlib import Path
from app.services.scheduler import DynamicScheduler

from app.core.config import config
from app.services.publick_functions import publick_post, send_recipe, send_fact
  
  
class ChannelsControl:
    channels = config.tg_channel.channel_names
    active_channel = channels[0]
    
    channels_autoposting = {
        channel: False
        for channel in channels
    }

    parsers = {
        '@best_tasty_recipes': send_recipe,
        '@world_of_amazing_facts': send_fact
    }
    

    schedulers = {
        name: DynamicScheduler(name, 
                               Path(config.tg_channel.schedule_path), 
                               publick_post,
                               args=[name]) 
        for name in config.tg_channel.channel_names
    }
    
    @classmethod
    def switch_autoposting(cls):
        cls.channels_autoposting[cls.active_channel] = not cls.channels_autoposting[cls.active_channel]
        if cls.channels_autoposting[cls.active_channel]:
            cls.schedulers[cls.active_channel].start()
        else:
            cls.schedulers[cls.active_channel].stop()

