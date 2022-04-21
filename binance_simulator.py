import binance

import config


class ClientMock:

    def __init__(self):
        self.api_key = config.api_key
        self.secret_key = config.secret_key

        self.balances = {"USDT": 500}
        binance.set(self.api_key, self.secret_key)

    def get_balances_simulated(self):
        return self.balances

    def get_balances(self):
        return binance.balances()

    def klines(self, pair, time_step, limit):
        return binance.klines(pair, time_step, limit=limit)

    def place_buy_order(self, symbol:str, qty, price):
        order = None


        actual_coin = symbol.replace("USDT", "")

        if self.balances["USDT"] >= qty:
            self.balances["USDT"] -= qty

            if actual_coin not in self.balances.keys():
                self.balances[actual_coin] = 0

            executedQty = qty / price
            self.balances[actual_coin] += executedQty
            order = {"executedQty": executedQty}
        else:
            order = {"executedQty": 0}

        return order

    def place_sell_order(self, symbol, qty, price):
        actual_coin = symbol.replace("USDT", "")
        price_in_usdt = price * qty

        self.balances["USDT"] += price_in_usdt
        self.balances[actual_coin] = 0

        order = {"executedQty": price_in_usdt}
        return order

    def emulate_place_sell_order(self, symbol, qty, price):
        actual_coin = symbol.replace("USDT", "")
        price_in_usdt = price * qty

        order = {"executedQty": price_in_usdt}
        return order