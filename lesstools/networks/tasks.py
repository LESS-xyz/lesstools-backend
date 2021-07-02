import time
import dramatiq
import requests
from .models import Network
from django.conf import settings
from lesstools.networks.api import process_native_txs, process_token_txs

@dramatiq.actor(max_retries=0)
def check_payment_address():
    for network in Network.objects.all():
        web3 = network.get_web3_connection()
        current_block = web3.eth.blockNumber
        print(f'start payment check in {network.name} from block {network.last_processed_block},'
              f' till block {current_block}')
        # get new native and token txs
        new_native_transactions = requests.get(
            network.native_api_url.format(address=settings.PAYMENT_ADDRESS,
                                          startblock=network.last_processed_block, endblock=current_block))
        if new_native_transactions.status_code == 200:
            process_native_txs(new_native_transactions.json())
        else:
            print('error on new native txs')
        # sleep to prevent etherscan rates limit
        time.sleep(6)
        new_token_transactions = requests.get(
            network.token_api_url.format(address=settings.PAYMENT_ADDRESS,
                                          startblock=network.last_processed_block, endblock=current_block))
        if new_token_transactions.status_code == 200:
            process_token_txs(new_token_transactions.json())
        else:
            print('error on getting token txs')
        network.last_processed_block = current_block
        network.save(update_fields=('last_processed_block',))