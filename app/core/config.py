from dataclasses import dataclass
from environs import Env

@dataclass
class TgBot:
    token: str
    admin_ids: list[str]
    
@dataclass
class TgChannel:
    channel_names: list[str]
    schedule_path: str
    
@dataclass
class Database:
    path: str
    
@dataclass
class Gemini:
    api_key: str
    model: str
    
@dataclass
class Config:
    tg_bot: TgBot
    tg_channel: TgChannel
    database: Database
    gemimi: Gemini
    
def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
            admin_ids=list(env.list('ADMIN_IDS')),
        ),
        tg_channel=TgChannel(
            channel_names=list(env.list('CHANNEL_IDS')),
            schedule_path=env('SCHEDULE_PATH')
        ),
        database=Database(
            path=env('DATABASE_PATH')
        ),
        gemimi=Gemini(
            api_key=env('GEMINI_API_KEY'),
            model=env('GEMINI_MODEL')
        )
    )

config = load_config()
