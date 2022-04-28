def get_binance_symbol_out_of_coin(coin):
    return coin + "USDT"


def get_coin_out_of_symbol(symbol: str):
    return symbol.replace("USDT", "")
