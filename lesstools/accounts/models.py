from django.db import models
from bip32utils import BIP32Key
from eth_keys import keys
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from datetime import timedelta

from lesstools.settings import ROOT_KEYS
from lesstools.consts import MAX_DIGITS

class AdvUser(AbstractUser):
    class plans(models.TextChoices):
        FREE = 'Free'
        STANDART = 'Standart'
        PREMIUM = 'Premium'
    plan = models.CharField(max_length=10, choices=plans.choices, default=plans.FREE)
    payment_address = models.CharField(max_length=50, null=True, default=None)
    # on dextools pair page has uniswap pair address in url, so i guess array of addresses should work
    favourite_pairs = ArrayField(models.CharField(max_length=50))

    def generate_keys(self):
        eth_root_public_key = ROOT_KEYS['ETH']['public']
        root_key = BIP32Key.fromExtendedKey(eth_root_public_key, public=True)
        child_key = root_key.ChildKey(self.id)
        self.payment_address = keys.PublicKey(child_key.K.to_string()).to_checksum_address().lower()
        self.save()


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
