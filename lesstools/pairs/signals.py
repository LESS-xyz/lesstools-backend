from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Pairs
from tgbot.handlers import new_pair


@receiver(post_save, sender=Pairs)
def send_message_to_telegram(sender, **kwargs):
    pair = kwargs['instance']
    pair_information = {
        'main_currence': pair.main_currency,
        'sub_currency': pair.sub_currency,
        'rating': pair.rating,
        'trust': pair.trust,
    }
    await new_pair(message='new_pair', pair=pair_information)
