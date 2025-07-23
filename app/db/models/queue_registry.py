from sqlalchemy import MetaData
from app.db.models.post_queue import create_post_queue_model
from app.services.user_data import users_data
from sqlalchemy import Table

metadata = MetaData()


class QueueRegistry:
    def __init__(self, metadata):
        self.metadata = metadata
        self.queue_tables = {}
        self.update_queue_tables()

    def update_queue_tables(self):
        current_channels = set(users_data.get_all_schedules().keys())
        # Remove tables for channels that no longer exist
        # for channel in list(self.queue_tables.keys()):
        #     if channel not in current_channels:
        #         del self.queue_tables[channel]
        # Add or update tables for current channels
        for channel in current_channels:
            if channel not in self.queue_tables:
                self.queue_tables[channel] = create_post_queue_model(
                    f'{channel[1:]}_queue', self.metadata
                )
                

tables_registry = QueueRegistry(metadata)

# Пример использования:
# registry = QueueRegistry(metadata)
# registry.update_queue_tables()
# queue_tables = registry.queue_tables
