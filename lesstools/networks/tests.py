import dramatiq
import pytest
from django_dramatiq.test import DramatiqTestCase
from django.conf import settings
from lesstools.accounts.models import PlanPayment
from lesstools.rates.models import UsdRate
from lesstools.networks.models import Network
import requests


@pytest.fixture
def broker():
    broker = dramatiq.get_broker()
    broker.flush_all()
    return broker


@pytest.fixture
def worker(broker):
    worker = dramatiq.Worker(broker, worker_timeout=100)
    worker.start()
    yield worker
    worker.stop()


class DramatiqTests(DramatiqTestCase):
    def test_networking_connection(self):
        for network in Network.objects.all():
            web3 = network.get_web3_connection()
            self.broker.join(web3.queue_name)
            self.worker.join()
            self.assertEqual(web3, True)

    def test_native_status_code(self):
        for network in Network.objects.all():
            web3 = network.get_web3_connection()
            current_block = web3.eth.blockNumber

            new_native_transactions = requests.get(
                network.native_api_url.format(address=settings.PAYMENT_ADDRESS,
                                              startblock=network.last_processed_block, endblock=current_block))
            self.assertEqual(new_native_transactions.status_code, 200)

    def test_token_status_code(self):
        for network in Network.objects.all():
            web3 = network.get_web3_connection()
            current_block = web3.eth.blockNumber

            new_token_transactions = requests.get(
                network.token_api_url.format(address=settings.PAYMENT_ADDRESS,
                                             startblock=network.last_processed_block, endblock=current_block))
            self.assertEqual(new_token_transactions.status_code, 200)

    def test_process_native_txs(self):
        for network in Network.objects.all():
            web3 = network.get_web3_connection()
            current_block = web3.eth.blockNumber
            new_native_transactions = requests.get(
                network.native_api_url.format(address=settings.PAYMENT_ADDRESS,
                                              startblock=network.last_processed_block, endblock=current_block))
            if new_native_transactions.get('status') == '1':
                for tx in new_native_transactions.get('result'):
                    self.assertNotEqual(tx['to'], tx['from'])
                    self.asserEqual(tx['to'], settings.PAYMENT_ADDRESS)
                    self.assertNotIn(tx['hash'], PlanPayment.objects.all().values('tx_hash'))
                    self.assertIn(network.name, UsdRate.objects.all().values('currency'))
