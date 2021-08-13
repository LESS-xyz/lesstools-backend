from django.db import models
from django.contrib.postgres.fields import ArrayField


class Token(models.Model):
    ETH_PLATFORM_CMC_ID = 1027
    BSC_PLATFORM_CMC_ID = 1839
    POLYGON_PLATFORM_CMC_ID = 3890

    cmc_id = models.PositiveSmallIntegerField(unique=True, null=True)
    cmc_slug = models.CharField(max_length=50, null=True)

    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=50)

    price_in_usd = models.DecimalField(max_digits=22, decimal_places=15, null=True)
    total_supply = models.DecimalField(max_digits=100, decimal_places=0, null=True)
    circulating_supply = models.DecimalField(max_digits=20, decimal_places=5, null=True)
    market_cap = models.DecimalField(max_digits=20, decimal_places=5, null=True)
    fully_diluted_market_cap = models.DecimalField(max_digits=20, decimal_places=5, null=True)
    holders_count = models.PositiveIntegerField(null=True)

    eth_address = models.CharField(max_length=50, null=True)
    bsc_address = models.CharField(max_length=50, null=True)
    polygon_address = models.CharField(max_length=50, null=True)

    website_url = models.CharField(max_length=100, null=True)
    chat_urls = ArrayField(models.CharField(max_length=100), null=True)
    twitter_url = models.CharField(max_length=100, null=True)
