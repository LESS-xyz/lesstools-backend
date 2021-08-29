from django.core.management.base import BaseCommand, CommandError
from apscheduler.schedulers.background import BlockingScheduler
import pytz

from lesstools.accounts.tasks import check_paid, check_hold, cancel_invalid_holdings
from lesstools.networks.tasks import check_payment_address
from lesstools.rates.tasks import update_rates
from lesstools.analytics.tasks import periodic_cmc_mapping_update


class Command(BaseCommand):
    help = 'Run blocking scheduler to create periodical tasks'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Preparing scheduler'))
        scheduler = BlockingScheduler(timezone=pytz.UTC)
        scheduler.add_job(check_paid.send, 'interval', seconds=300)
        scheduler.add_job(check_hold.send, 'interval', seconds=300)
        # check for networks which become unsupported for holding or removed
        scheduler.add_job(cancel_invalid_holdings.send, 'interval', hours=1)
        scheduler.add_job(update_rates.send, 'interval', seconds=300)
        scheduler.add_job(check_payment_address.send, 'interval', seconds=60)
        scheduler.add_job(periodic_cmc_mapping_update.send, 'interval', days=1)
        # ... add another jobs
        self.stdout.write(self.style.NOTICE('Start scheduler'))
        scheduler.start()
