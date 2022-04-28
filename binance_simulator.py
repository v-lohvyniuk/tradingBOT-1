import os
import sys
import time

import config
import db.client as db
import utils.stringutils as strutils
from binance import client

os.environ['TZ'] = 'Europe/Kiev'
if sys.platform != "win32":
    time.tzset()


class ClientMock:

    def __init__(self):
        self.api_key = config.api_key
        self.secret_key = config.secret_key
        self.balanceDAO = db.BalanceDAO()
        self.orderDAO = db.OrderDAO()

        self.balances = {"USDT": config.STARTING_BALANCE}

        self.client = client.Client(self.api_key, self.secret_key)

    def get_balances_simulated(self):
        return self.balances

    def get_balance_simulated(self, currency):
        return self.balanceDAO.get_balance(currency=currency)

    def get_balances_simulated_from_db(self):
        return self.balanceDAO.get_balances()

    def get_order_history(self):
        return self.orderDAO.get_orders()

    def get_balances(self):
        pass
        # return self.client.balances()

    def klines(self, pair, time_step, limit):
        return self.client.get_klines(symbol=pair, interval=time_step, limit=limit)

    def place_buy_order(self, symbol: str, usdt_qty, price):
        order = None

        actual_coin = symbol.replace("USDT", "")
        usdt_balance = self.get_balance_simulated("USDT").amount

        if usdt_balance >= usdt_qty:

            buying_amount = usdt_qty / price
            usdt_left = usdt_balance - usdt_qty
            self.balanceDAO.set_balance(currency=strutils.get_coin_out_of_symbol(symbol), amount=buying_amount)
            self.balanceDAO.set_balance(currency="USDT", amount=usdt_left)

            order = db.Order(time=time.ctime(),
                             is_buy=True,
                             coin=actual_coin,
                             price=price,
                             usdt_price=usdt_qty)

            self.orderDAO.put_order(order)

            order = {"executedQty": buying_amount}
        else:
            order = {"executedQty": 0}

        return order

    def place_sell_order(self, symbol, qty, price):
        coin = strutils.get_coin_out_of_symbol(symbol)
        price_in_usdt = price * qty

        usdt_balance = self.balanceDAO.get_balance("USDT")
        usdt_balance += price_in_usdt

        self.balanceDAO.set_balance(currency="USDT", amount=usdt_balance)
        self.balanceDAO.set_balance(currency=coin, amount=0.0)

        order = db.Order(time=time.ctime(),
                         is_buy=False,
                         coin=coin,
                         price=price,
                         usdt_price=price_in_usdt)

        self.orderDAO.put_order(order)

        order = {"executedQty": price_in_usdt}
        return order

    def emulate_place_sell_order(self, symbol, qty, price):
        actual_coin = symbol.replace("USDT", "")
        price_in_usdt = price * qty

        order = {"executedQty": price_in_usdt}
        return order

    def flush(self):
        self.balanceDAO.delete_all_balances()
        self.orderDAO.delete_all_orders()

        self.balanceDAO.set_balance("USDT", config.STARTING_BALANCE)
