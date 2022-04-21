import binance

import config


class Client:

    def __init__(self):
        self.api_key = config.api_key
        self.secret_key = config.secret_key

        binance.set(self.api_key, self.secret_key)

    def balances(self):
        return binance.balances()

    def klines(self, pair, time_step, limit):
        return binance.klines(pair, time_step, limit=limit)

    def place_buy_order(self, symbol, qty, price):
        return binance.order(symbol=symbol, side="BUY", orderType="MARKET", quantity=qty, price=price)

    def place_sell_order(self, symbol, qty, price):
        return binance.order(symbol=symbol, side="SELL", orderType="MARKET", quantity=qty, price=price)



