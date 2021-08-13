import os
import django
import logging

from setting_env import BOT_TOKEN
from aiogram import Bot, Dispatcher


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lesstools.settings')
os.environ.update({'DJANGO_ALLOW_ASYNC_UNSAFE': 'true'})
django.setup()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
DP = Dispatcher(bot)
SKIP_UPDATES = True
TIMEOUT = 20
