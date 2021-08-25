from web3 import Web3
from django.db import models
from web3.middleware import geth_poa_middleware

from lesstools.rates.models import UsdRate


class Network(models.Model):
    LESS_TOKEN_DECIMALS = 10 ** 18

    name = models.CharField(max_length=100)
    endpoint = models.CharField(max_length=200)
    last_processed_block = models.IntegerField(default=1)
    needs_poa_middleware = models.BooleanField(default=False)
    native_api_url = models.CharField(max_length=400)
    token_api_url = models.CharField(max_length=400)

    native_token = models.ForeignKey('PaymentToken', on_delete=models.RESTRICT, related_name='NOT_NEEDED+')

    allows_holding_for_paid_plans = models.BooleanField(default=False)
    less_token_address = models.CharField(max_length=128)

    def get_web3_connection(self):
        web3 = Web3(Web3.HTTPProvider(self.endpoint))
        if self.needs_poa_middleware:
            web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        return web3


class PaymentToken(models.Model):
    network = models.ForeignKey('Network', on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=128)

    currency = models.CharField(max_length=100, help_text='Currency name for CoinGecko rates')
    coingecko_code = models.CharField(max_length=100)
    decimals = models.IntegerField(default=18)

    usd_rate = models.ForeignKey('rates.UsdRate', on_delete=models.RESTRICT, editable=False)

    def save(self, *args, **kwargs):
        usd_rate, _ = UsdRate.objects.get_or_create(currency=self.currency)
        usd_rate.save()
        self.usd_rate = usd_rate
        super(PaymentToken, self).save(*args, **kwargs)

    def __str__(self):
        return self.currency
