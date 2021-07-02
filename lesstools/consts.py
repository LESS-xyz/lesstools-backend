MAX_DIGITS = len(str(2 ** 256))

# TODO move decimals to rates model and check decimals from contract
DECIMALS = {
    'USD': 10 ** 2,
    'USDC': 10 ** 6,
    'ethereum': 10 ** 18,
    'binance-smart-chain': 10 ** 18,
    'WBNB': 10 ** 18,

}