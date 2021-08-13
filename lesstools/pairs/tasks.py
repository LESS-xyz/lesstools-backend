import dramatiq
from tgbot.handlers import new_pair


@dramatiq.actor(max_retries=0)
def send_message_to_telegram(**kwargs):
    pair = kwargs['instance']
    pair_information = {
        'main_currence': pair.main_currency,
        'sub_currency': pair.sub_currency,
        'rating': pair.rating,
        'trust': pair.trust,
    }
    await new_pair(message='new_pair', pair=pair_information)
