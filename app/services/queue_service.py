from sqlalchemy import insert, select, delete, desc
from app.db.session import AsyncSessionLocal
from app.db.models.queue_registry import tables_registry


async def add_post(channel: str, post_text: str, image_url: str = None, video_url: str = None):
    table = tables_registry.queue_tables[channel]
    
    async with AsyncSessionLocal() as session:
        await session.execute(insert(table).values(post_text=post_text, image_url=image_url, video_url=video_url))
        await session.commit()
        
        
async def get_next_post_and_delete(channel: str):
    table = tables_registry.queue_tables[channel]
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(table).limit(1))
        post = result.fetchone()
        
        if post:
            await session.execute(delete(table).where(table.c.id == post.id))
            await session.commit()
            
    return post


async def get_next_post(channel: str):
    table = tables_registry.queue_tables[channel]
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(table).limit(1))
        post = result.fetchone()
    return post


async def get_last_post_and_delete(channel: str):
    table = tables_registry.queue_tables[channel]
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(table).order_by(desc(table.c.id)).limit(1))
        post = result.fetchone()
        
        if post:
            await session.execute(delete(table).where(table.c.id == post.id))
            await session.commit()
            
    return post


async def get_last_post(channel: str):
    table = tables_registry.queue_tables[channel]
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(table).order_by(desc(table.c.id)).limit(1))
        post = result.fetchone()
    return post



async def get_queue(channel: str):
    table = tables_registry.queue_tables[channel]
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(table))
        posts = result.fetchall()
    return posts

