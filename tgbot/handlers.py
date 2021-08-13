from aiogram import types
from tgbot.settings import DP


@DP.message_handler(commands=['new_pair'])
async def new_pair(message: types.Message, **kwargs):
    """Send new pair"""
    await message.reply("New pair")
    values = kwargs.get('pair')
    await message.reply(f'{values["sub_currency"]} |  @{values["main_currency"]} ({values["sub_currency"]}/{values["main_currency"]}\n)'
                        f'Initial Liquidity: ${values["liquidity"]}\n'
                        f'Token contract: {values["token_contract"]}\n'
                        f'DEXTools: {values["pair_url"]}')
