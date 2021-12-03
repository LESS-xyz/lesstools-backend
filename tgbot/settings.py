import os
import django
import logging

from lesstools.settings import BOT_TOKEN
from aiogram import Bot, Dispatcher
import telebot

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
os.environ.update({'DJANGO_ALLOW_ASYNC_UNSAFE': 'true'})
django.setup()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = telebot.TeleBot(token=BOT_TOKEN, parse_mode=None)    # todo change to actual token
#DP = Dispatcher(bot)
#SKIP_UPDATES = True
#TIMEOUT = 20
