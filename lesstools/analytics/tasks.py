import dramatiq
from .api import mapping_update


@dramatiq.actor(max_retries=0)
def periodic_cmc_mapping_update():
    print('starting CoinMarketCap mapping update')
    mapping_update()
    print('ending CoinMarketCap mapping update')
