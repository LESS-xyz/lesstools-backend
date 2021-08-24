import dramatiq
from django.utils import timezone
from .models import AdvUser
import logging


@dramatiq.actor(max_retries=0)
def check_paid():
    logging.info('starting paid check')

    for user in AdvUser.objects.exclude(plan=AdvUser.Plans.FREE):
        # for every user with active plan check if payment end time is expired and downgrade him
        active_payments = user.payments.filter(end_time__gte=timezone.now()).count()
        if active_payments == 0:
            user.plan = AdvUser.Plans.FREE
        elif active_payments == 1:
            user.plan = AdvUser.Plans.STANDARD
        else:
            continue

        user.save()
        logging.info(f'payment of {user.username} is expired, downgrading to {user.plan} plan')

    logging.info('ending paid check')
