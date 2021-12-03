import logging

import dramatiq
from .api import mapping_update
from .models import NewPairCount


@dramatiq.actor(max_retries=0)
def periodic_cmc_mapping_update():
    logging.info('starting CoinMarketCap mapping update')
    mapping_update()
    logging.info('ending CoinMarketCap mapping update')


#  todo move to signals when implementing new pairs tgbot (it's just an example from Semyon)
# @receiver(post_save, sender=Pairs)
# def send_message_to_telegram(sender, **kwargs):
#     pair = kwargs['instance']
#     pair_information = {
#         'main_currence': pair.main_currency,
#         'sub_currency': pair.sub_currency,
#         'rating': pair.rating,
#         'trust': pair.trust,
#     }
#     await new_pair(message='new_pair', pair=pair_information)

@dramatiq.actor(max_retries=0)
def check_new_pair():
    for swap in NewPairCount.objects.all():
        swap_check(swap.name)
