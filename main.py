import asyncio
from app.bot.bot_main import start_bot
from app.services.db_initializer import init_channels_tables


async def main():
    await init_channels_tables()
    await asyncio.gather(
        start_bot()
    )

if __name__ == "__main__":
    asyncio.run(main())