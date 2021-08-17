from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from datetime import timedelta

from lesstools.consts import MAX_DIGITS


class PlanPrice(models.Model):
    """PlanPayment price. Free->Premium=2x price"""
    price = models.PositiveSmallIntegerField(blank=False, help_text='You should have only one price record,'
                                                                    ' and should not delete it.'
                                                                    'It is Standard plan price.'
                                                                    'Premium is assumed to be 2x bigger')


class AdvUser(AbstractUser):
    class Plans(models.TextChoices):
        FREE = 'Free'
        STANDARD = 'Standard'
        PREMIUM = 'Premium'

    plan = models.CharField(max_length=10, choices=Plans.choices, default=Plans.FREE)
    # Users' favorite pairs
    # on dextools pair page has uniswap pair address in url, so i guess array of addresses should work
    favourite_pairs = ArrayField(models.CharField(max_length=50), null=True)
    # favourite_pairs = models.ForeignKey(Pairs, on_delete=models.CASCADE, null=True)


class PlanPayment(models.Model):
    user = models.ForeignKey(AdvUser, on_delete=models.CASCADE, related_name='payments')
    payment_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)
    tx_hash = models.CharField(max_length=128)
    amount = models.DecimalField(max_digits=MAX_DIGITS, decimal_places=0)
    currency = models.CharField(max_length=10)

    def get_end_time(self):
        self.end_time = self.payment_time + timedelta(days=30)
        self.save()
