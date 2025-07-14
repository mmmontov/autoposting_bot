from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import config

DATABASE_URL = f'sqlite+aiosqlite:///{config.database.path}'

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

