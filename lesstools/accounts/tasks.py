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

    for user in AdvUser.objects.exclude(plan_by_payments=AdvUser.Plans.FREE):
        old_plan = user.plan_by_payments

        # for every user with active plan check if payment end time has come and downgrade him
        active_payments = user.payments.filter(end_time__gte=timezone.now())
        if active_payments.count() == 0:
            user.plan_by_payments = AdvUser.Plans.FREE
        elif active_payments.count() == 1:
            if active_payments.first().grants_plan == AdvUser.Plans.STANDARD:
                user.plan_by_payments = AdvUser.Plans.STANDARD
            elif active_payments.first().grants_plan == AdvUser.Plans.PREMIUM:
                user.plan_by_payments = AdvUser.Plans.PREMIUM
        else:
            continue

        user.save()
        if old_plan != user.plan_by_payments:
            logging.info(f'payment of {user.username} is expired, downgrading to {user.plan_by_payments} plan')

    logging.info('ending paid check')


@dramatiq.actor(max_retries=0)
def check_hold():
    logging.info('starting hold check')

    needed_amount = PlanPrice.objects.all().first().holding_amount_in_less
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

            old_plan = user.plan_by_holding

            if user_holding_amount >= 2 * needed_amount:
                user.plan_by_holding = AdvUser.Plans.PREMIUM
            elif user_holding_amount >= needed_amount:
                user.plan_by_holding = AdvUser.Plans.STANDARD
            else:
                user.plan_by_holding = AdvUser.Plans.FREE

            user.save()

            if old_plan != user.plan_by_holding:
                logging.info(f'{user.username} is now holding {user_holding_amount} in LESS, '
                             f'new plan - {user.plan_by_holding}')

    logging.info('ending hold check')


@dramatiq.actor(max_retries=0)
def cancel_invalid_holdings():
    logging.info('starting invalid holdings check')

    for user in AdvUser.objects.exclude(plan_by_holding=AdvUser.Plans.FREE):
        has_supported_networks = False
        for holding_obj in user.holds.all():
            if holding_obj.network.allows_holding_for_paid_plans:
                has_supported_networks = True
                break

        if not has_supported_networks:
            user.plan_by_holding = AdvUser.Plans.FREE
            user.save()
            logging.info(f'plan by holding of {user} has been downgraded, cause some networks became unsupported')

    logging.info('ending invalid holdings check')
