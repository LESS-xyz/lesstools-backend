import logging

import requests
from python_graphql_client import GraphqlClient

from web3 import Web3

from lesstools.analytics.models import Token
from lesstools.settings import CMC_COIN_INFO_API_URL, CMC_MAP_API_URL, CMC_API_KEY, ETHPLORER_API_KEY, \
    ETHPLORER_TOKEN_INFO_API_URL

from django.db.models import Q
from django.utils import timezone

CMC_PAGE_SIZE = 10000


def mapping_update(run_full_update=False):
    cmc_request = requests.get(CMC_MAP_API_URL, headers={'X-CMC_PRO_API_KEY': CMC_API_KEY})
    if cmc_request.status_code == 200:
        data = cmc_request.json()['data']
    else:
        logging.error('error on CMC data retrieval')
        raise RuntimeError()

    paginate_from = 1
    while len(data) > 0:
        for token in data:
            if token['platform'] is not None:
                json_address = token['platform']['token_address']
                # just because sometimes tokens listed on CMC could have something different from pure hex string
                try:
                    normalized_address = Web3.toChecksumAddress(
                        json_address[json_address.index('0x'):json_address.index('0x') + 42])
                except ValueError:
                    # or could have no hex string at all (like Binance Chain IDs, useless slug and so on)
                    normalized_address = None
            else:
                normalized_address = None

            if run_full_update:
                possible_eth_address = normalized_address if (normalized_address is not None and
                                                              token['platform']['id'] == Token.ETH_PLATFORM_CMC_ID) else None
                possible_bsc_address = normalized_address if (normalized_address is not None and
                                                              token['platform']['id'] == Token.BSC_PLATFORM_CMC_ID) else None
                possible_polygon_address = normalized_address if (normalized_address is not None and
                                                                  token['platform']['id'] == Token.POLYGON_PLATFORM_CMC_ID) else None

                # cause all these fields in Q are unique,
                # we should not try creating new one, if not such cmc_id exists, but addresses do
                Token.objects.update_or_create(Q(cmc_id=token['id']) |
                                               Q(eth_address=possible_eth_address) |
                                               Q(bsc_address=possible_bsc_address) |
                                               Q(polygon_address=possible_polygon_address),
                                               defaults={
                                                   'name': token['name'],
                                                   'symbol': token['symbol'],
                                                   'eth_address': possible_eth_address,
                                                   'bsc_address': possible_bsc_address,
                                                   'polygon_address': possible_polygon_address})
            elif not Token.objects.filter(cmc_id=token['id']).exists():
                Token(cmc_id=token['id'],
                      name=token['name'],
                      symbol=token['symbol'],
                      eth_address=normalized_address if (normalized_address is not None and
                                                         token['platform'][
                                                             'id'] == Token.ETH_PLATFORM_CMC_ID) else None,
                      bsc_address=normalized_address if (normalized_address is not None and
                                                         token['platform'][
                                                             'id'] == Token.BSC_PLATFORM_CMC_ID) else None,
                      polygon_address=normalized_address if (normalized_address is not None and
                                                             token['platform'][
                                                                 'id'] == Token.POLYGON_PLATFORM_CMC_ID) else None).save()

        paginate_from += CMC_PAGE_SIZE
        cmc_request = requests.get(CMC_MAP_API_URL, headers={'X-CMC_PRO_API_KEY': CMC_API_KEY},
                                   params={'start': paginate_from})
        if cmc_request.status_code == 200:
            data = cmc_request.json()['data']
        else:
            logging.error('error on CMC data retrieval')
            raise RuntimeError()


def try_extend_if_needed(token: Token, platform: str):
    if platform == 'ETH' and token.eth_address is not None:
        ethplorer_request = requests.get(ETHPLORER_TOKEN_INFO_API_URL.format(address=token.eth_address),
                                         params={'apiKey': ETHPLORER_API_KEY})
        if ethplorer_request.status_code == 200:
            data = ethplorer_request.json()
        else:
            logging.error('error on Ethplorer data retrieval')
            return token

        if token.price_in_usd is None or token.price_in_usd == 0:
            token.price_in_usd = data['price']['rate'] if (
                        data['price'] and data['price']['currency'] == 'USD') else None
        if token.total_supply is None or token.total_supply == 0:
            token.total_supply = data['totalSupply']
        if token.holders_count is None or token.holders_count == 0:
            token.holders_count = data['holdersCount']
        if token.website_url is None:
            token.website_url = data['website'] if 'website' in data else None
        if token.chat_urls is None:
            token.chat_urls = [data['telegram']] if 'telegram' in data else None
        if token.twitter_url is None:
            token.twitter_url = 'https://twitter.com/' + data['twitter'] if 'twitter' in data else None

    # todo data extension for other platforms

    token.save()

    return token


def info_from_ethplorer(token_address):
    ethplorer_request = requests.get(ETHPLORER_TOKEN_INFO_API_URL.format(address=token_address),
                                     params={'apiKey': ETHPLORER_API_KEY})
    if ethplorer_request.status_code == 200:
        data = ethplorer_request.json()
    else:
        logging.error('error on Ethplorer data retrieval')
        return None

    token, created = Token.objects.update_or_create(eth_address=token_address, defaults={
        'name': data['name'],
        'symbol': data['symbol'],
        'price_in_usd': data['price']['rate'] if (data['price'] and data['price']['currency'] == 'USD') else None,
        'total_supply': data['totalSupply'],
        'holders_count': data['holdersCount'],
        'website_url': data['website'] if 'website' in data else None,
        'chat_urls': [data['telegram']] if 'telegram' in data else None,
        'twitter_url': 'https://twitter.com/' + data['twitter'] if 'twitter' in data else None,
    })

    if created:
        logging.info(f'token "{token.symbol}" saved to the database')

    return token


def info_from_cmc(token_address, token_name, token_symbol, platform):
    if platform == 'ETH' and Token.objects.filter(eth_address=token_address).exists():
        token = Token.objects.get(eth_address=token_address)
    elif platform == 'BSC' and Token.objects.filter(bsc_address=token_address).exists():
        token = Token.objects.get(bsc_address=token_address)
    elif platform == 'POLYGON' and Token.objects.filter(polygon_address=token_address).exists():
        token = Token.objects.get(polygon_address=token_address)
    #     implies that CoinMarketCap doesn't have coins with both same name & symbol
    elif Token.objects.filter(name=token_name, symbol=token_symbol).exists():
        token = Token.objects.get(name=token_name, symbol=token_symbol)
    else:
        return None

    # not listed on CMC but has been added before via some other API
    if token.cmc_id is None:
        return None

    cmc_request = requests.get(CMC_COIN_INFO_API_URL.format(coin_id=token.cmc_id))
    if cmc_request.status_code == 200:
        data = cmc_request.json()['data']
    else:
        logging.error('error on CMC data retrieval')
        return None

    if 'platforms' in data:
        for platform in data['platforms']:
            json_address = platform['contractAddress']
            # just because sometimes tokens listed on CMC could have something different from pure hex string
            try:
                normalized_address = Web3.toChecksumAddress(
                    json_address[json_address.index('0x'):json_address.index('0x') + 42])
            except ValueError:
                # or could have no hex string at all (like Binance Chain IDs, useless slug and so on)
                normalized_address = None

            if platform['contractId'] == Token.ETH_PLATFORM_CMC_ID:
                token.eth_address = normalized_address
            elif platform['contractId'] == Token.BSC_PLATFORM_CMC_ID:
                token.bsc_address = normalized_address
            elif platform['contractId'] == Token.POLYGON_PLATFORM_CMC_ID:
                token.polygon_address = normalized_address

    token.cmc_slug = data['slug']

    if 'statistics' in data:
        token.price_in_usd = data['statistics']['price']
        token.total_supply = data['statistics']['totalSupply']
        token.fully_diluted_market_cap = data['statistics']['fullyDilutedMarketCap']
        token.circulating_supply = data['statistics']['circulatingSupply']
        token.market_cap = data['statistics']['marketCap']

    if 'holders' in data:
        token.holders_count = data['holders']['holderCount']

    if 'urls' in data:
        token.website_url = data['urls']['website'][0] if len(data['urls']['website']) > 0 else None
        token.chat_urls = data['urls']['chat'] if len(data['urls']['chat']) > 0 else None
        token.twitter_url = data['urls']['twitter'][0] if len(data['urls']['twitter']) > 0 else None

    token.save()

    return token


def candles_creater(pair_id, url, time_interval):
    client = GraphqlClient(endpoint=url)

    now = int(timezone.now().timestamp())
    time = {
        'minute': 60,
        'hour': 60 * 60,
        'day': 60 * 60 * 24,
        'week': 60 * 60 * 24 * 7,
        'month': 60 * 60 * 24 * 30
    }

    t = {'end': now,
         'start': now - time[time_interval]}
    limits = []
    for x in range(0, 240):
        limits.append([t['end'], t['start']])
        t['end'] = t['start']
        t['start'] -= time[time_interval]

    query = """
        {
            pairs(where: {id: "%s"}) {
                id
                swaps(where: {timestamp_gte: "%s"}, orderBy: timestamp, orderDirection: desc) {
                    timestamp
                    token0PriceUSD
                    token0PriceETH
                    token1PriceUSD
                    token1PriceETH
                }
            }
        }
    """ % (pair_id, limits[-1][1])

    response_data = client.execute(query=query)

    candles = []
    cache = []
    for limit in limits:
        for r in response_data['data']['pairs'][0]['swaps']:
            if limit[0] >= int(r['timestamp']) > limit[1]:
                cache.append({
                    'timestamp': r['timestamp'],
                    'token0PriceUSD': r['token0PriceUSD'],
                    'token0PriceETH': r['token0PriceETH'],
                    'token1PriceUSD': r['token1PriceUSD'],
                    'token1PriceETH': r['token1PriceETH'],
                })
        candles.append(cache)
        cache = []

    result = []
    usd_list_for_sort = []
    times = {}
    count = 0
    for candle in candles:
        for swap in candle:
            usd_list_for_sort.append(swap['token1PriceUSD'])
            times[swap['timestamp']] = swap['token1PriceUSD']
        sort = sorted(usd_list_for_sort)
        sorted_tuple = sorted(times.items(), key=lambda x: x[0])
        if len(usd_list_for_sort) > 0 and len(candles[count]):
            result.append(dict(**candles[count][0], **{'high': sort[-1], 'low': sort[0],
                                                       'start': sorted_tuple[0], 'end': sorted_tuple[-1]}))
        else:
            result.append('')
        count += 1
        usd_list_for_sort = []
    candle = {}
    time_count = 0
    for x in result:
        try:
            candle[str(time_count)] = {
                'start_time': limits[time_count][0],
                'end_time': limits[time_count][1],
                'start': x['start'],
                'end': x['end'],
                'high': x['high'],
                'low': x['low']
            }
        except:
            candle[str(time_count)] = {
                'start_time': limits[time_count][0],
                'end_time': limits[time_count][1],
                'start': ' ',
                'end': ' ',
                'high': ' ',
                'low': ' '
            }
        time_count += 1
    return candle
