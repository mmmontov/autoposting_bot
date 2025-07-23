from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable
from app.core.utils import ChannelsControl  

class UserAccessMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = data.get("event_from_user")
        if user:
            user_id = user.id
            swap_post = ChannelsControl.get_swap_post_status(user_id)
            regenerate_post = ChannelsControl.get_regenerate_post_status(user_id)
            can_swap_channel = ChannelsControl.get_can_channel_swap(user_id)

            # ✅ добавляем параметр для хендлера
            data["swap_post"] = swap_post
            data["regenerate_post"] = regenerate_post
            data["can_swap_channel"] = can_swap_channel

        return await handler(event, data)
