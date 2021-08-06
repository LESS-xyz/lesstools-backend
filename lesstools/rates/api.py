from lesstools.rates.models import UsdRate
from lesstools.settings import QUERY_TSYMS
from lesstools.consts import DECIMALS


def get_usd_prices():
    usd_prices = {currency: UsdRate.objects.get(currency=currency).rate for currency in QUERY_TSYMS.keys()}
    print('current rates {usd_prices}', flush=True)

    return usd_prices


def calculate_amount(original_amount, from_currency, to_currency='USD'):
    print(f'Calculating amount, original: {original_amount}, from {from_currency} to {to_currency}', flush=True)

    usd_rates = get_usd_prices()
    if to_currency == 'USD':
        currency_rate = usd_rates[from_currency]
    else:
        currency_rate = usd_rates[from_currency] / usd_rates[to_currency]
    amount = int(int(original_amount) / DECIMALS[from_currency] * DECIMALS[to_currency] * float(currency_rate))

    return amount, currency_rate