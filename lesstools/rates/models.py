from django.db import models

from lesstools.consts import MAX_DIGITS


class UsdRate(models.Model):
    """
    Model that store coingecko token rates and info for coingecko requests
    """
    currency = models.CharField(max_length=100, unique=True)
    rate = models.DecimalField(max_digits=MAX_DIGITS, decimal_places=2, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.currency
