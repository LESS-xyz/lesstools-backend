from aiogram import executor
from settings import DP, SKIP_UPDATES, TIMEOUT


if __name__ == '__main__':
    executor.start_polling(DP, timeout=TIMEOUT, skip_updates=SKIP_UPDATES)
