import asyncio
import json
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from typing import Callable
from app.core.config import config

def load_schedule(chanel):
    schedule_path = config.tg_channel.schedule_path
    
    with open(schedule_path, encoding='utf-8') as f:
        data = json.load(f)[chanel]
        return data.get('schedule', [])
    return []

def update_schedule(channel, data: list): 
    schedule_path = config.tg_channel.schedule_path
    with open(schedule_path, encoding='utf-8') as f:
        all_data = json.load(f)
        all_data[channel]['schedule'] = data
    with open(schedule_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

class DynamicScheduler:
    def __init__(self, name: str, json_path: Path, job_func: Callable, args: list):
        self.args = args
        self.name = name
        self.json_path = json_path
        self.scheduler = AsyncIOScheduler()
        self.job_func = job_func
        self._last_hash = None
        self._watcher_task = None

    def _generate_job_id(self, time_str: str) -> str:
        return f"{self.name}_{time_str.replace(':', '_')}"

    def load_schedule_data(self):
        with self.json_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def reschedule_jobs(self):
        data = self.load_schedule_data()
        self.scheduler.remove_all_jobs()
        
        schedule_type = data.get(self.name)
        if schedule_type:
            for time_str in schedule_type['schedule']:
                hour, minute = map(int, time_str.split(":"))
                self.scheduler.add_job(
                    self.job_func,
                    CronTrigger(hour=hour, minute=minute),
                    id=self._generate_job_id(time_str),
                    args=self.args
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
                print(f"[{self.name}] Ошибка при чтении JSON: {e}")
            await asyncio.sleep(5)

    def start(self):
        if not self.scheduler.running:
            self.reschedule_jobs()
            self.scheduler.start()
            self._watcher_task = asyncio.create_task(self._watch_json_file())
            print(f"{self.name} запущен.")

    def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            if self._watcher_task:
                self._watcher_task.cancel()
            print(f"{self.name} остановлен.")


