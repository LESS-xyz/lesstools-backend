from aiogram import types
from tgbot.settings import DP
from settings import bot


#@DP.message_handler(commands=['new_pair'])
#async def new_pair(message: types.Message, **kwargs):
#    """Send new pair"""
 #   await message.reply("New pair")
  #  values = kwargs.get('pair')
   # await message.reply(f'{values["name"]} |  @{values["symbol"]} ({values["price_in_usd"]}/{values["total_supply"]}\n)'
    #                    f'Holders: ${values["holders_count"]}\n'
     #                   f'Token contract: {values["website_url"]}\n'
      #                  f'DEXTools: {values["chat_urls"]}')
@bot.message_handler(commands=['new_pair'])
def new_pair(message, **kwargs)
    bot.send_message(TELEGRAM_CHAT_ID, f'{values["name"]} |  @{values["symbol"]} ({values["price_in_usd"]}/{values["total_supply"]}\n)'
                        f'Holders: ${values["holders_count"]}\n'
                        f'Token contract: {values["website_url"]}\n'
                        f'DEXTools: {values["chat_urls"]}')

