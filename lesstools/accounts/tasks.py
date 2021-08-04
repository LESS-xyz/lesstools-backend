import dramatiq
from django.utils import timezone
from .models import AdvUser


@dramatiq.actor(max_retries=0)
def check_paid():
    print('starting paid check')
    for user in AdvUser.objects.exclude(plan=AdvUser.plans.FREE):
        # for every user with active plan check if payment end time is expired and downgrade him
        if not user.payments.filter(end_time__gte=timezone.now()):
            user.plan = AdvUser.plans.FREE
            user.save()
            print(f'payment of {user.username} is expired, downgrading')
    print('ending paid check')
