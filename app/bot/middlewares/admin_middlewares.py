from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable
from app.core.config import config


class AdminOnlyMiddleware(BaseMiddleware):
    def __init__(self):
        self.admin_ids = list(map(int, config.tg_bot.admin_ids))

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if event.from_user.id not in self.admin_ids:
            await event.answer("⛔️ У вас нет доступа к этой команде.")
            return  # прерываем цепочку
        return await handler(event, data)
