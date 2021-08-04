import sys
import dramatiq
import json
import requests
import traceback

from lesstools.rates.models import UsdRate
from lesstools.settings import QUERY_TSYMS, QUERY_FSYM, API_URL


def get_rates(fsym, tsym, reverse=False):
    res = requests.get(API_URL.format(coin_code=tsym))
    if res.status_code != 200:
        raise Exception('cannot get exchange rate for {}'.format(fsym))
    answer = json.loads(res.text)
    if reverse:
        answer = answer['market_data']['current_price'][fsym]

    return answer


@dramatiq.actor(max_retries=0)
def update_rates():
    usd_prices = {}

    try:
        for tsym, tsym_code in QUERY_TSYMS.items():
            usd_prices[tsym] = get_rates(QUERY_FSYM, tsym_code, reverse=True)
    except Exception as e:
        print('\n'.join(traceback.format_exception(*sys.exc_info())), flush=True)
        return

    # Lock usdt prices to USD cause here cause idk where else
    usd_prices['USDT'] = 1

    print(f'new usd prices {usd_prices}', flush=True)

    for currency, price in usd_prices.items():
        try:
            rate_object = UsdRate.objects.get(currency=currency)
        except UsdRate.DoesNotExist:
            rate_object = UsdRate(currency=currency)

        rate_object.rate = price
        rate_object.save()

    print('saved ok', flush=True)
