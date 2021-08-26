import logging

import requests

from web3 import Web3

from lesstools.analytics.models import Token
from lesstools.settings import CMC_COIN_INFO_API_URL, CMC_MAP_API_URL, CMC_API_KEY, ETHPLORER_API_KEY, \
    ETHPLORER_TOKEN_INFO_API_URL

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
                Token.objects.update_or_create(cmc_id=token['id'], defaults={
                    'name': token['name'],
                    'symbol': token['symbol'],
                    'eth_address': normalized_address if (normalized_address is not None and
                                                          token['platform']['id'] == Token.ETH_PLATFORM_CMC_ID) else None,
                    'bsc_address': normalized_address if (normalized_address is not None and
                                                          token['platform']['id'] == Token.BSC_PLATFORM_CMC_ID) else None,
                    'polygon_address': normalized_address if (normalized_address is not None and
                                                              token['platform']['id'] == Token.POLYGON_PLATFORM_CMC_ID) else None})
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
            token.price_in_usd = data['price']['rate'] if (data['price'] and data['price']['currency'] == 'USD') else None
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
