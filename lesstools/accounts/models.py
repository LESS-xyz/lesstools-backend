from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from datetime import timedelta

from lesstools.consts import MAX_DIGITS

class AdvUser(AbstractUser):
    class plans(models.TextChoices):
        FREE = 'Free'
        STANDART = 'Standart'
        PREMIUM = 'Premium'
    plan = models.CharField(max_length=10, choices=plans.choices, default=plans.FREE)
    # on dextools pair page has uniswap pair address in url, so i guess array of addresses should work
    favourite_pairs = ArrayField(models.CharField(max_length=50))



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
