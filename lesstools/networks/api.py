from django.utils import timezone
from django.conf import settings
from lesstools.networks.models import PaymentToken
from lesstools.accounts.models import AdvUser, PlanPayment
from lesstools.rates.api import calculate_amount
from lesstools.rates.models import UsdRate
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


def process_native_txs(native_txs, network):
    if native_txs.get('status') == '1':
        for tx in native_txs.get('result'):
            # check and exclude not valid txs
            if not is_applicable(tx):
                continue

            logging.info(tx)

            user = AdvUser.objects.filter(username=tx['from']).first()

            usd_amount, _ = calculate_amount(tx['value'], network.native_token.currency)

            logging.info(f'usd_amount: {usd_amount}')
            payment = PlanPayment.objects.create(
                user=user, payment_time=timezone.now(), tx_hash=tx['hash'],
                amount=tx['value'], token_used=network.native_token
            )
            payment.get_end_time()
            price = PlanPrice.objects.all().first().price
            # allow at least 1% difference if less and 5% if more
            # todo change type to decimal?
            if float(price) * 0.99 <= usd_amount <= float(price) * 1.05:
                if user.plan == AdvUser.Plans.FREE:
                    user.plan = AdvUser.Plans.STANDARD
                elif user.plan == AdvUser.Plans.STANDARD:
                    user.plan = AdvUser.Plans.PREMIUM
            elif float(2 * price) * 0.99 <= usd_amount <= float(2 * price) * 1.05 and user.plan == AdvUser.Plans.FREE:
                user.plan = AdvUser.Plans.PREMIUM
            else:
                logging.error(f"{usd_amount} not acceptable for changing the plan, {price} or {2 * price} is needed")
                continue
            user.save()
            logging.info(f"{user} has changed plan successfully")
    else:
        print('no new native txs')


def process_token_txs(token_txs):
    if token_txs.get('status') == '1':
        for tx in token_txs.get('result'):
            # check and exclude not valid txs
            if not is_applicable(tx, is_token_tx=True):
                continue

            logging.info(tx)

            user = AdvUser.objects.filter(username=tx['from']).first()
            token = PaymentToken.objects.filter(address__iexact=tx['contractAddress']).first()
            usd_amount, _ = calculate_amount(tx['value'], token.currency)

            # TODO compare usd_amount with plan prices
            logging.info(f'usd_amount: {usd_amount}')
            payment = PlanPayment.objects.create(
                user=user, payment_time=timezone.now(), tx_hash=tx['hash'],
                amount=tx['value'], token_used=token
            )
            payment.get_end_time()
            price = PlanPrice.objects.all().first().price
            # todo allow at least 1% difference if less and 5% if more
            if usd_amount == price:
                if user.plan == AdvUser.Plans.FREE:
                    user.plan = AdvUser.Plans.STANDARD
                elif user.plan == AdvUser.Plans.STANDARD:
                    user.plan = AdvUser.Plans.PREMIUM
            elif usd_amount == 2 * price and user.plan == AdvUser.Plans.FREE:
                user.plan = AdvUser.Plans.PREMIUM
            else:
                logging.error(f"{usd_amount} not acceptable for changing the plan, {price} or {2*price} is needed")
                continue
            user.save()
            logging.info(f"{user} has changed plan successfully")

    else:
        logging.info('no new token txs')
