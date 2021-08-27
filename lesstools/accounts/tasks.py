import dramatiq
from django.utils import timezone
from .models import AdvUser, PlanPrice, UserHolding
import logging

from web3 import Web3

from lesstools.networks.models import Network
from lesstools.accounts.abis.balance_of_LESS import ABI


@dramatiq.actor(max_retries=0)
def check_paid():
    logging.info('starting paid check')

    for user in AdvUser.objects.exclude(plan=AdvUser.Plans.FREE):
        old_plan = user.plan

        # for every user with active plan check if payment end time has come and downgrade him
        active_payments = user.payments.filter(end_time__gte=timezone.now())
        if active_payments.count() == 0:
            user.plan = AdvUser.Plans.FREE
        elif active_payments.count() == 1:
            if active_payments.first().grants_plan == AdvUser.Plans.STANDARD:
                user.plan = AdvUser.Plans.STANDARD
            elif active_payments.first().grants_plan == AdvUser.Plans.PREMIUM:
                user.plan = AdvUser.Plans.PREMIUM
        else:
            continue

        user.save()
        if old_plan != user.plan:
            logging.info(f'payment of {user.username} is expired, downgrading to {user.plan} plan')

    logging.info('ending paid check')


@dramatiq.actor(max_retries=0)
def check_hold():
    logging.info('starting hold check')

    needed_amount = PlanPrice.objects.all().first().holding_amount_in_less
    # todo if network does not allow holding - cancel
    for network in Network.objects.filter(allows_holding_for_paid_plans=True):
        web3 = network.get_web3_connection()
        less_token_contract = web3.eth.contract(Web3.toChecksumAddress(network.less_token_address), abi=ABI)
        for user in AdvUser.objects.all():
            try:
                user_address = Web3.toChecksumAddress(user.username)
            except ValueError:
                continue

            user_holding_amount = \
                less_token_contract.functions.balanceOf(user_address).call() // Network.LESS_TOKEN_DECIMALS

            user_holding, _ = UserHolding.objects.get_or_create(user=user, network=network)
            user_holding.less_holding_amount = user_holding_amount
            user_holding.save()

            # not downgrade non-holding users with active monthly subscriptions
            active_payments = user.payments.filter(end_time__gte=timezone.now())

            old_plan = user.plan

            if user_holding_amount >= 2 * needed_amount:
                user.plan = AdvUser.Plans.PREMIUM
            elif user_holding_amount >= needed_amount:
                if active_payments.count() >= 2 or (active_payments.exists() and
                                                    active_payments.first().grants_plan == AdvUser.Plans.PREMIUM):
                    user.plan = AdvUser.Plans.PREMIUM
                else:
                    user.plan = AdvUser.Plans.STANDARD
            else:
                if active_payments.count() >= 2 or (active_payments.exists() and
                                                    active_payments.first().grants_plan == AdvUser.Plans.PREMIUM):
                    user.plan = AdvUser.Plans.PREMIUM
                elif active_payments.count() == 1:
                    user.plan = AdvUser.Plans.STANDARD
                else:
                    user.plan = AdvUser.Plans.FREE

            user.save()

            if old_plan != user.plan:
                logging.info(f'{user.username} is now holding {user_holding_amount} in LESS, new plan - {user.plan}')

    logging.info('ending hold check')
