from django.core.management.base import BaseCommand, CommandError
from lesstools.analytics.models import NewPairCount
from lesstools.settings import SWAP


class Command(BaseCommand):
    help = 'Create start data'

    def handle(self, *args, **options):
        for name in SWAP:
            if name == 'pancakeswap':
                NewPairCount.objects.update_or_create(name=name, count=23298)
            elif name == 'mdex_bsc':
                NewPairCount.objects.update_or_create(name=name, count=1138)
            elif name == 'joetrader':
                NewPairCount.objects.update_or_create(name=name, count=1015)
            elif name == 'honeyswap':
                NewPairCount.objects.update_or_create(name=name, count=1768)
            elif name == 'biswap':
                NewPairCount.objects.update_or_create(name=name, count=470)
            elif name == 'babyswap':
                NewPairCount.objects.update_or_create(name=name, count=770)
            else:
                NewPairCount.objects.update_or_create(name=name, count=2000)
