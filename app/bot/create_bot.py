from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from app.core.config import config
from aiogram.enums import ParseMode


bot = Bot(config.tg_bot.token, default=DefaultBotProperties(parse_mode='HTML'))