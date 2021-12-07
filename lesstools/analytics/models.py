from django.db import models
from django.contrib.postgres.fields import ArrayField

from lesstools.accounts.models import AdvUser


class Token(models.Model):
    ETH_PLATFORM_CMC_ID = 1027
    BSC_PLATFORM_CMC_ID = 1839
    POLYGON_PLATFORM_CMC_ID = 3890
    FANTOM_PLATFORM_CMC_ID = 3513
    XDAI_PLATFORM_CMC_ID = 5601
    AVALANCHE_PLATFORM_CMC_ID = 5805

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

    eth_address = models.CharField(max_length=50, unique=True, null=True)
    bsc_address = models.CharField(max_length=50, unique=True, null=True)
    polygon_address = models.CharField(max_length=50, unique=True, null=True)
    fantom_address = models.CharField(max_length=50, unique=True, null=True)
    xdai_address = models.CharField(max_length=50, unique=True, null=True)
    avalanche_address = models.CharField(max_length=50, unique=True, null=True)

    website_url = models.CharField(max_length=100, null=True)
    chat_urls = ArrayField(models.CharField(max_length=100), null=True)
    twitter_url = models.CharField(max_length=100, null=True)


class Pair(models.Model):
    class Platforms(models.TextChoices):
        ETH_PLATFORM = 'ETH'
        BSC_PLATFORM = 'BSC'
        POLYGON_PLATFORM = 'POLYGON'
        XDAY_PLATFORM = 'XDAY'
        FANTOM_PLATFORM = 'FANTOM'
        AVALANCHE_PLATFORM = 'AVALANCHE'

    address = models.CharField(max_length=50)
    platform = models.CharField(max_length=10, choices=Platforms.choices)

    class Meta:
        unique_together = ('address', 'platform',)

    # the **bold** one, analytics of which are shown on the Pair Explorer
    # does not necessary reflect pair base/quote in contract
    # can be Null if no additional token's info can be retrieved
    token_being_reviewed = models.ForeignKey(to=Token, on_delete=models.RESTRICT, null=True)


class UserPairVote(models.Model):
    LIKE = 1
    DISLIKE = -1
    NEUTRAL = 0

    VOTES = (
        (DISLIKE, 'Dislike'),
        (LIKE, 'Like'),
        (NEUTRAL, 'Neutral')
    )

    vote = models.SmallIntegerField(choices=VOTES, editable=False, default=NEUTRAL)
    user = models.ForeignKey(AdvUser, on_delete=models.RESTRICT, related_name='votes')
    pair = models.ForeignKey(Pair, on_delete=models.RESTRICT, related_name='votes')

    class Meta:
        unique_together = ('user', 'pair',)


class NewPairCount(models.Model):
    name = models.CharField(max_length=64)
    count = models.PositiveIntegerField()


class HotPairManager(models.Model):
    name = models.CharField(max_length=16)
    address = models.CharField(max_length=128)
    image = models.FileField(upload_to='images/')


class MainToken(models.Model):
    name = models.CharField(max_length=16)
    address = models.CharField(max_length=128)
    image = models.FileField(upload_to='images/')
