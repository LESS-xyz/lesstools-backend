from django.core.management.base import BaseCommand, CommandError
from apscheduler.schedulers.background import BlockingScheduler
import pytz

from lesstools.accounts.tasks import check_paid
from lesstools.networks.tasks import check_payment_address
from lesstools.rates.tasks import update_rates


class Command(BaseCommand):
    help = 'Run blocking scheduler to create periodical tasks'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Preparing scheduler'))
        scheduler = BlockingScheduler(timezone=pytz.UTC)
        scheduler.add_job(check_paid.send, 'interval', seconds=300)
        scheduler.add_job(update_rates.send, 'interval', seconds=300)
        scheduler.add_job(check_payment_address.send, 'interval', seconds=60)
        # ... add another jobs
        self.stdout.write(self.style.NOTICE('Start scheduler'))
        scheduler.start()
