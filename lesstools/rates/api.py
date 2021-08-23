from lesstools.networks.models import PaymentToken
from lesstools.rates.models import UsdRate
import logging


def get_usd_prices():
    usd_prices = {rate_object.currency: rate_object.rate for rate_object in UsdRate.objects.all()}
    logging.info(f'current rates {usd_prices}')

    return usd_prices


def calculate_amount(original_amount, from_currency, to_currency='USD'):
    logging.info(f'Calculating amount, original: {original_amount}, from {from_currency} to {to_currency}')

    usd_rates = get_usd_prices()
    if to_currency == 'USD':
        currency_rate = usd_rates[from_currency]
    else:
        currency_rate = usd_rates[from_currency] / usd_rates[to_currency]

    from_token = PaymentToken.objects.filter(currency=from_currency).first()
    # it seems that multiplying by to_currency.decimals shouldn't be used here
    amount = int(int(original_amount) / (10 ** from_token.decimals) * float(currency_rate))

    return amount, currency_rate
