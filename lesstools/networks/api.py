from django.utils import timezone
from django.conf import settings
from lesstools.networks.models import PaymentToken
from lesstools.accounts.models import AdvUser, PlanPayment
from lesstools.rates.api import calculate_amount
from lesstools.accounts.models import PlanPrice
import logging


def is_applicable(tx, is_token_tx: bool = False):
    if tx['to'].lower() != settings.PAYMENT_ADDRESS.lower() or tx['to'] == tx['from']:
        logging.info(f"{tx.get('hash')}: found outcoming tx or loop tx, skipping")
        return False
    if not AdvUser.objects.filter(username=tx['from']).exists():
        logging.info(f"{tx.get('hash')}: tx from unknown user, skipping")
        return False
    if PlanPayment.objects.filter(tx_hash=tx['hash']).exists():
        logging.info(f"{tx.get('hash')}: tx_hash already processed, skipping")
        return False

    if is_token_tx and not PaymentToken.objects.filter(address__iexact=tx['contractAddress']).exists():
        logging.info(f"{tx.get('hash')}: tx with not accepted token, skipping")
        return False

    return True


def apply_payment(tx, network=None):
    logging.info(tx)

    user = AdvUser.objects.filter(username=tx['from']).first()
    token = PaymentToken.objects.filter(address__iexact=tx['contractAddress']).first() \
        if network is None else network.native_token
    usd_amount, _ = calculate_amount(tx['value'], token.currency)

    logging.info(f'usd_amount: {usd_amount}')
    payment = PlanPayment.objects.create(
        user=user, payment_time=timezone.now(), tx_hash=tx['hash'],
        amount=tx['value'], token_used=token
    )

    price = PlanPrice.objects.all().first().monthly_price_in_usd
    # allow at least 5% difference due to the volatile rates
    if float(price) * 0.95 <= usd_amount <= float(price) * 1.05:
        if user.plan == AdvUser.Plans.FREE:
            user.plan = AdvUser.Plans.STANDARD
            payment.grants_plan = AdvUser.Plans.STANDARD
        elif user.plan == AdvUser.Plans.STANDARD:
            user.plan = AdvUser.Plans.PREMIUM
            payment.grants_plan = AdvUser.Plans.PREMIUM
    elif float(2 * price) * 0.95 <= usd_amount <= float(2 * price) * 1.05:
        user.plan = AdvUser.Plans.PREMIUM
        payment.grants_plan = AdvUser.Plans.PREMIUM
    else:
        payment.define_end_time(successful=False)
        logging.error(f"{usd_amount} not acceptable for changing the plan, {price} or {2 * price} is needed")
        return

    user.save()
    payment.define_end_time(successful=True)
    logging.info(f"{user} has changed plan successfully")


def process_native_txs(native_txs, network):
    if native_txs.get('status') == '1':
        for tx in native_txs.get('result'):
            # check and exclude not valid txs
            if not is_applicable(tx):
                continue

            apply_payment(tx, network)
    else:
        logging.info('no new native txs')


def process_token_txs(token_txs):
    if token_txs.get('status') == '1':
        for tx in token_txs.get('result'):
            # check and exclude not valid txs
            if not is_applicable(tx, is_token_tx=True):
                continue

            apply_payment(tx)
    else:
        logging.info('no new token txs')
