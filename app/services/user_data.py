import asyncio
import aiofiles
import json
import os
from datetime import datetime

from app.core.config import config


class AsyncUserDataStore:
    def __init__(self, filename=config.database.users_path):
        self.filename = filename
        self.data = {}
        self.lock = asyncio.Lock()
        self._load_sync()

    def _load_sync(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            self._last_modified = os.path.getmtime(self.filename)
        else:
            self.data = {}
            self._last_modified = 0

    async def _watch_file_changes(self, interval: float = 5):
        while True:
            await asyncio.sleep(interval)
            try:
                current_modified = os.path.getmtime(self.filename)
                if current_modified != self._last_modified:
                    async with self.lock:
                        self._load_sync()
                        print(f"[{datetime.now()}] Файл {self.filename} был обновлён, данные перезагружены.")
            except Exception as e:
                print(f"[watcher error]: {e}")

    def start_watching(self):
        if not hasattr(self, "_watch_task") or self._watch_task.done():
            self._watch_task = asyncio.create_task(self._watch_file_changes())

    async def _save(self):
        async with aiofiles.open(self.filename, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(self.data, indent=4, ensure_ascii=False))

    # Обеспечиваем наличие пользователя и канала
    def _ensure_user_channel(self, user_id: str, channel_id: str, name: str | None = None):
        user_id = str(user_id)
        user = self.data.setdefault(user_id, {
            "name": name,
            "active_channel": channel_id,
            "channels": {}
        })
        if "name" not in user:
            user["name"] = name
        if "active_channel" not in user:
            user["active_channel"] = channel_id
        if "channels" not in user:
            user["channels"] = {}
        user["channels"].setdefault(str(channel_id), {
            'autoposting': False,
            'parsing': False,
            'schedule': []
        })

    # Добавляем канал пользователя, создаём пользователя если нет
    async def add_user_channel(self, user_id: str, channel_id: str, name: str | None = None):
        user_id = str(user_id)
        async with self.lock:
            self._ensure_user_channel(user_id, channel_id, name)
            await self._save()

    # Удаляем пользователя и все его каналы
    async def delete_user(self, user_id: str):
        user_id = str(user_id)
        async with self.lock:
            if user_id in self.data:
                del self.data[user_id]
                await self._save()

    # Удаляем канал пользователя
    async def delete_user_channel(self, user_id: str, channel_id: str):
        user_id = str(user_id)
        async with self.lock:
            user = self.data.get(user_id)
            if user and "channels" in user and channel_id in user["channels"]:
                del user["channels"][channel_id]
                if user.get("active_channel") == channel_id:
                    user["active_channel"] = None
                await self._save()

    # Изменяем статус автопостинга канала
    async def set_autoposting(self, user_id: str, channel_id: str, status: bool):
        user_id = str(user_id)
        async with self.lock:
            self._ensure_user_channel(user_id, channel_id)
            self.data[user_id]["channels"][channel_id]['autoposting'] = status
            await self._save()
            return True

    # Получаем статус автопостинга пользователя
    def get_autoposting(self, user_id: str, channel_id: str) -> bool | None:
        user_id = str(user_id)
        return self.data.get(user_id, {}).get("channels", {}).get(channel_id, {}).get('autoposting')

    # Изменяем статус парсинга канала пользователя
    async def set_parsing(self, user_id: str, channel_id: str, status: bool):
        user_id = str(user_id)
        async with self.lock:
            self._ensure_user_channel(user_id, channel_id)
            self.data[user_id]["channels"][channel_id]['parsing'] = status
            await self._save()

    # Получаем статус парсинга канала пользователя
    def get_parsing(self, user_id: str, channel_id: str) -> bool | None:
        user_id = str(user_id)
        return self.data.get(user_id, {}).get("channels", {}).get(channel_id, {}).get('parsing')

    # Устанавливаем расписание пользователя
    async def set_schedule(self, user_id: str, channel_id: str, schedule: list[str]):
        user_id = str(user_id)
        async with self.lock:
            self._ensure_user_channel(user_id, channel_id)
            self.data[user_id]["channels"][channel_id]['schedule'] = schedule
            await self._save()

    # Получаем расписание пользователя
    def get_schedule(self, user_id: str | int, channel_id: str) -> list[str] | None:
        user_id = str(user_id)
        return self.data.get(user_id, {}).get("channels", {}).get(channel_id, {}).get('schedule')

    # Получаем все каналы пользователя
    def get_user_channels(self, user_id: str) -> list[str]:
        user_id = str(user_id)
        return list(self.data.get(user_id, {}).get("channels", {}).keys())

    # Получаем все расписания пользователей
    def get_all_schedules(self) -> dict[str, list[str]]:
        result = {}
        for user in self.data.values():
            channels = user.get("channels", {})
            for channel, settings in channels.items():
                result[channel] = settings.get('schedule', [])
        return result

    # Получаем значения autoposting всех каналов
    def get_channels_autoposting(self) -> dict[str, bool]:
        result = {}
        for user in self.data.values():
            channels = user.get("channels", {})
            for channel, settings in channels.items():
                result[channel] = settings.get('autoposting', False)
        return result

    # Получаем активный канал пользователя
    def get_active_channel(self, user_id: str) -> str | None:
        user_id = str(user_id)
        active_channel = self.data.get(user_id, {}).get("active_channel")
        if active_channel:
            return active_channel
        
        channels = self.data.get(user_id, {}).get("channels", {})
        if channels:
            first_channel = next(iter(channels.keys()))
            self.data[user_id]["active_channel"] = first_channel
            asyncio.create_task(self.set_active_channel(user_id, first_channel))


    # Устанавливаем активный канал пользователя
    async def set_active_channel(self, user_id: str, channel_id: str):
        user_id = str(user_id)
        async with self.lock:
            self._ensure_user_channel(user_id, channel_id)
            self.data[user_id]["active_channel"] = channel_id
            await self._save()
            

    # Получить имя пользователя
    def get_user_name(self, user_id: str) -> str | None:
        user_id = str(user_id)
        return self.data.get(user_id, {}).get("name")

    # Установить имя пользователя
    async def set_user_name(self, user_id: str, name: str):
        user_id = str(user_id)
        async with self.lock:
            if user_id not in self.data:
                self.data[user_id] = {
                    "name": name,
                    "active_channel": None,
                    "channels": {}
                }
            else:
                self.data[user_id]["name"] = name
            await self._save()


    # получить всех пользователей
    def get_all_user_ids(self) -> list[str]:
        return list(self.data.keys())

users_data = AsyncUserDataStore()