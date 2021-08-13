from aiogram import types
from settings import dp


@dp.message_handler(commands=['new_transaction'])
async def new_transaction(message: types.Message, **kwargs):
    """Send info about new transaction"""
    await message.reply("New transaction")
    values = kwargs.get('transaction')
    await message.reply(f'User: {values["user_name"]}\n'
                        f'Amount: {values["amount"]}\n'
                        f'tx_hash: {values["tx_hash"]}\n'
                        f'Currency: {values["currency"]}\n')
