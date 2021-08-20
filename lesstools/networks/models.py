from web3 import Web3
from django.db import models
from web3.middleware import geth_poa_middleware


class Network(models.Model):
    name = models.CharField(max_length=100)
    endpoint = models.CharField(max_length=200)
    last_processed_block = models.IntegerField(default=1)
    needs_poa_middleware = models.BooleanField(default=False)
    native_api_url = models.CharField(max_length=400)
    token_api_url = models.CharField(max_length=400)
    native_decimals = models.IntegerField(default=18)

    def get_web3_connection(self):
        web3 = Web3(Web3.HTTPProvider(self.endpoint))
        if self.needs_poa_middleware:
            web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        return web3


class Token(models.Model):
    network = models.ForeignKey('Network', on_delete=models.CASCADE)
    rate = models.ForeignKey('rates.UsdRate', on_delete=models.CASCADE)
    address = models.CharField(max_length=128)
