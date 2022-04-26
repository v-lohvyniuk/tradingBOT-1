from binance import client

import config
import time
import os
import sys

os.environ['TZ'] = 'Europe/Kiev'
if sys.platform != "win32":
    time.tzset()


class ClientMock:

    def __init__(self):
        self.api_key = config.api_key
        self.secret_key = config.secret_key

        self.balances = {"USDT": 500}
        self.order_history = []
        self.client = client.Client(self.api_key, self.secret_key)

    def get_balances_simulated(self):
        return self.balances

    def get_balances(self):
        pass
        # return self.client.balances()

    def klines(self, pair, time_step, limit):
        return self.client.get_klines(symbol=pair, interval=time_step, limit=limit)

    def place_buy_order(self, symbol:str, usdt_qty, price):
        order = None

        actual_coin = symbol.replace("USDT", "")

        if self.balances["USDT"] >= usdt_qty:
            self.balances["USDT"] -= usdt_qty

            if actual_coin not in self.balances.keys():
                self.balances[actual_coin] = 0

            executedQty = usdt_qty / price
            self.balances[actual_coin] += executedQty
            self.order_history.append([time.ctime(), "BUY", actual_coin, "COIN Price=" + str(price), "USDT spent=" + str(usdt_qty)])
            order = {"executedQty": executedQty}
        else:
            order = {"executedQty": 0}

        return order

    def place_sell_order(self, symbol, qty, price):
        actual_coin = symbol.replace("USDT", "")
        price_in_usdt = price * qty

        self.balances["USDT"] += price_in_usdt
        self.balances[actual_coin] = 0

        self.order_history.append([time.ctime(), "SELL", actual_coin, "COIN Price=" + str(price), "USDT gained=" + str(price_in_usdt)])

        order = {"executedQty": price_in_usdt}
        return order

    def emulate_place_sell_order(self, symbol, qty, price):
        actual_coin = symbol.replace("USDT", "")
        price_in_usdt = price * qty

        order = {"executedQty": price_in_usdt}
        return order