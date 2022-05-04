from db.client import Order


class BacktestResults:

    def __init__(self):
        self.final_usdt = None
        self.buy_points = []
        self.sell_points = []
        self.buy_orders = []
        self.sell_orders = []
        self.orders = []

    def add_buy_order(self, order: Order):
        self.buy_orders.append(order)
        self.orders.append(order)

        self.buy_points.append((order.time, order.price))

    def add_sell_order(self, order: Order):
        self.sell_orders.append(order)
        self.orders.append(order)

        self.sell_points.append((order.time, order.price))

    def set_final_usdt_result(self, result):
        self.final_usdt = result

class HistoricalDataItem:

    def __init__(self, price, date, rsi):
        self.price = price
        self.date = date
        self.rsi = rsi
