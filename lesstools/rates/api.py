from lesstools.rates.models import UsdRate
from lesstools.settings import QUERY_TSYMS
from lesstools.consts import DECIMALS
import logging


def get_usd_prices():
    usd_prices = {currency: UsdRate.objects.get(currency=currency).rate for currency in QUERY_TSYMS.keys()}
    logging.info(f'current rates {usd_prices}')

    return usd_prices


def calculate_amount(original_amount, from_currency, to_currency='USD'):
    logging.info(f'Calculating amount, original: {original_amount}, from {from_currency} to {to_currency}')

    usd_rates = get_usd_prices()
    if to_currency == 'USD':
        currency_rate = usd_rates[from_currency]
    else:
        currency_rate = usd_rates[from_currency] / usd_rates[to_currency]
    # it seems that multiplying by DECIMALS[to_currency] shouldn't be used here
    amount = int(int(original_amount) / DECIMALS[from_currency] * float(currency_rate))

    return amount, currency_rate
