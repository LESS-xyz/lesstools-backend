import dramatiq
from django.utils import timezone
from .models import AdvUser
import logging


@dramatiq.actor(max_retries=0)
def check_paid():
    logging.info('starting paid check')
    for user in AdvUser.objects.exclude(plan=AdvUser.Plans.FREE):
        # for every user with active plan check if payment end time is expired and downgrade him
        if not user.payments.filter(end_time__gte=timezone.now()):
            user.plan = AdvUser.Plans.FREE
            user.save()
            logging.info(f'payment of {user.username} is expired, downgrading')
    logging.info('ending paid check')
