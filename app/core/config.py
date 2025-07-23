from dataclasses import dataclass
from environs import Env

@dataclass
class TgBot:
    token: str
    admin_ids: list[str]
    
@dataclass
class Database:
    path: str
    users_path: str
    
@dataclass
class OpenRouter:
    api_key: str
    base_url: str
    model: str
    
@dataclass
class Config:
    tg_bot: TgBot
    database: Database
    open_router: OpenRouter
    
def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
            admin_ids=list(env.list('ADMIN_IDS')),
        ),
        database=Database(
            path=env('DATABASE_PATH'),
            users_path=env('USERS_PATH')
        ),
        open_router=OpenRouter(
            api_key=env('OPENROUTER_API_KEY'),
            base_url=env('OPENROUTER_BASE_URL'),
            model=env('OPENROUTER_MODEL')
        )
    )

config = load_config()
