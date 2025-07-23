from app.db.models.queue_registry import metadata
from app.db.session import engine

async def init_channels_tables():
    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_con: metadata.create_all(sync_con))
        
