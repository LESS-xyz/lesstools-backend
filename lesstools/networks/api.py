from django.utils import timezone
from django.conf import settings
from lesstools.networks.models import Token
from lesstools.accounts.models import AdvUser, PlanPayment
from lesstools.rates.api import calculate_amount


def process_native_txs(native_txs):
    if native_txs.get('status') == '1':
        #TODO nearly same logic as in process_token_txs (except accepted_coin logic)
        print(native_txs['result'][0])
    else:
        print('no new native txs')


def process_token_txs(token_txs):
    if token_txs.get('status') == '1':
        for tx in token_txs.get('result'):
            print(tx)
            # Check and exclude not valid txs
            if tx['to'].lower() != settings.PAYMENT_ADDRESS.lower() or tx['to'] == tx['from']:
                print(f"{tx.get('hash')}: found outcoming tx or loop tx, skipping")
                continue
            accepted_coin = Token.objects.filter(address__iexact=tx['contractAddress']).first()
            if not accepted_coin:
                print(f"{tx.get('hash')}: tx with not accepted token, skipping")
                continue
            user = AdvUser.objects.filter(username=tx['from']).first()
            if not user:
                print(f"{tx.get('hash')}: tx from unknown user ,skipping")
                continue
            if PlanPayment.objects.filter(tx_hash=tx['hash']).exists():
                print(f"{tx.get('hash')}: tx_hash already processed, skipping")
                continue
            usd_amount = calculate_amount(tx['value'], accepted_coin.rate.currency)
            #TODO compare usd_amount with plan prices
            #TODO what to do with underpayment and overpayment?
            print(f'usd_amount: {usd_amount}')
            payment = PlanPayment.objects.create(
                user=user, payment_time=timezone.now(), tx_hash=tx['hash'],
                amount=tx['value'], currency=tx['tokenSymbol']
            )
            #TODO upgrade from plans.STANDART to plans.PREMIUM?
            if user.plan == AdvUser.plans.FREE:
                user.plan = AdvUser.plans.PREMIUM
                user.save()

    else:
        print('no new token txs')
