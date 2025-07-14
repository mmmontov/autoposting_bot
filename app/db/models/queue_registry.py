from sqlalchemy import MetaData
from app.db.models.post_queue import create_post_queue_model
from app.core.config import config

metadata = MetaData()

queue_tables = {
    channel: create_post_queue_model(f'{channel[1:]}_queue', metadata)
    for channel in config.tg_channel.channel_names
}