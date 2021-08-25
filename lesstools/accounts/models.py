from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta

from lesstools.consts import MAX_DIGITS


class PlanPrice(models.Model):
    """Plan payment price and holding amount"""
    monthly_price_in_usd = models.PositiveSmallIntegerField(help_text='You should have only one price record for payments,'
                                                               ' and should not delete it.\n'
                                                               'It is Standard plan price.'
                                                               ' Premium is assumed to be 2x more expensive.')

    holding_amount_in_less = models.PositiveIntegerField(help_text='You should have only one amount record for holding,'
                                                           ' and should not delete it.\n'
                                                           'It is holding amount for Standard plan.'
                                                           ' Premium is assumed to be 2x bigger.')


class AdvUser(AbstractUser):
    class Plans(models.TextChoices):
        FREE = 'Free'
        STANDARD = 'Standard'
        PREMIUM = 'Premium'

    plan = models.CharField(max_length=10, choices=Plans.choices, default=Plans.FREE)
    # avoiding circular import error
    favourite_pairs = models.ManyToManyField('analytics.Pair', blank=True, related_name='favourite_of')


class PlanPayment(models.Model):
    user = models.ForeignKey(AdvUser, on_delete=models.CASCADE, related_name='payments')
    payment_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True,
                                    help_text='If end time equals payment time - the payment was unsuccessful '
                                              'and user did not upgrade')
    tx_hash = models.CharField(max_length=128)
    amount = models.DecimalField(max_digits=MAX_DIGITS, decimal_places=0)
    token_used = models.ForeignKey('networks.PaymentToken', null=True, blank=True, on_delete=models.SET_NULL)

    def define_end_time(self, successful: bool):
        self.end_time = self.payment_time + timedelta(days=30) if successful else self.payment_time
        self.save()
