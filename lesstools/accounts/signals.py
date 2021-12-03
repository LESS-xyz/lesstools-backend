import logging

from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from .models import PlanPayment, PlanPrice, AdvUser
from rest_framework.exceptions import APIException
from admintgbot.handlers import new_transaction


@receiver(post_save, sender=PlanPayment)
def send_message_to_telegram(sender, **kwargs):
    """Send to admin telegram bot information about new transaction"""
    new_transactions = kwargs['instance']
    new_transaction_information = {
        'user_name': new_transactions.user.username,
        'amount': new_transactions.amount,
        'tx_hash': new_transactions.tx_hash,
        'currency': new_transactions.currency,
    }
    print('START SIGNAL')
    await new_transaction(message='new_transaction', transaction=new_transaction_information)


@receiver(pre_delete, sender=PlanPrice)
def delete_locked(sender, **kwargs):
    """Protection against deletion price"""
    logging.error('you can not delete price')
    raise APIException


# probably unnecessary
@receiver(pre_save, sender=AdvUser)
def check_count_favorite_pairs(sender, **kwargs):
    """Check users' favorite pairs limit"""
    user = kwargs['instance']
    if len(user.favorite_pairs) >= 10 and \
            user.plan_by_payments == AdvUser.Plans.FREE and user.plan_by_holding == AdvUser.Plans.FREE:
        logging.error(f'{user.username} have limit 10 or less favorite pairs!')
        raise APIException
    else:
        pass
