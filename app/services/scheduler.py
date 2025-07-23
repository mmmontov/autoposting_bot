import asyncio
import json
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from typing import Callable

from app.core.config import config
from app.services.user_data import users_data


class DynamicScheduler:
    def __init__(self, name: str, json_path: Path, job_func: Callable):
        self.name = name
        self.json_path = json_path
        self.scheduler = AsyncIOScheduler()
        self.job_func = job_func
        self._last_hash = None
        self._watcher_task = None

    def _generate_job_id(self, time_str: str) -> str:
        return f"{self.name}_{time_str.replace(':', '_')}"

    def reschedule_jobs(self):
        data = users_data.get_all_schedules()
        self.scheduler.remove_all_jobs()
        
        schedule_type = data.get(self.name)
        if schedule_type:
            for time_str in schedule_type:
                hour, minute = map(int, time_str.split(":"))
                self.scheduler.add_job(
                    self.job_func,
                    CronTrigger(hour=hour, minute=minute),
                    id=self._generate_job_id(time_str),
                    args=[self.name]
                )
            print(f"[{datetime.now()}] {self.name}: задачи пересозданы.")
            

    async def _watch_json_file(self):
        while self.scheduler.running:
            try:
                current_hash = hash(self.json_path.read_text())
                if current_hash != self._last_hash:
                    self._last_hash = current_hash
                    self.reschedule_jobs()
            except Exception as e:
                print(f"[{datetime.now()}] {self.name} Ошибка при чтении JSON: {e}")
            await asyncio.sleep(5)

    def start(self):
        if not self.scheduler.running:
            self.reschedule_jobs()
            self.scheduler.start()
            self._watcher_task = asyncio.create_task(self._watch_json_file())
            print(f"[{datetime.now()}] {self.name} запущен.")

    def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            if self._watcher_task:
                self._watcher_task.cancel()
            print(f"[{datetime.now()}] {self.name} остановлен.")


