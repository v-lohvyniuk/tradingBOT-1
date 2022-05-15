import datetime

import algorithms.algorithm
import config

POLLING_TIME = 60

import threading
import time
import pandas as pd
from flask import Flask, redirect, url_for
import binance_wrapper
import layout
import os
import layout.page
import db.client as db
from db.client import Order
import utils.stringutils as strutils

binance = binance_wrapper.Client()
orderDAO = db.OrderDAO()
app = Flask(__name__)

is_thread_started = False
trading_pause = False

client = binance_wrapper.Client()
# client = binance_simulator.ClientMock()

LIMIT = 100

USDT_BUY_THESHOLD = 5


def get_hourly_data(symbol):
    return binance.get_historical_data(symbol, "1h", limit=LIMIT)


def check_and_buy(usdt_balance, coin, historical_data, index, algorithm, orders):
    is_able_to_buy = usdt_balance > USDT_BUY_THESHOLD
    if is_able_to_buy and not orders[-1].is_buy:
        algo_return = algorithm(historical_data, index, check_condition="BUY", orders=orders)
        should_buy = algo_return.should_buy()
        if should_buy:
            spent_cost = usdt_balance
            bought_coin = spent_cost / historical_data["prices"][index]
            deal_exact_time = datetime.datetime.now()
            order = client.place_buy_order(coin, bought_coin)
            client.wait_for_order_status(order["orderId"], coin, ["FULFILLED", "FILLED"])

            print(
                f"[{deal_exact_time}]  Bought coin {coin} at price {historical_data['prices'][index]} with RSI {historical_data['RSI'][index]}")
            order = Order(time=deal_exact_time, is_buy=True, coin=coin, price=historical_data['prices'][index],
                          usdt_price=spent_cost, reason=algo_return.get_reason())
            return order


def check_and_sell(coin, historical_data, index, algorithm, orders):
    algo_return = algorithm(historical_data, index, check_condition="SELL", orders=orders)
    should_sell = algo_return.should_sell()
    coin_balance = float(client.balance(coin.replace("USDT", ""))['free'])

    if should_sell and coin_balance > 0.01:
        deal_exact_time = datetime.datetime.now()

        order = client.place_sell_order(coin, coin_balance)
        client.wait_for_order_status(order["orderId"], coin, ["FULFILLED", "FILLED"])

        gained_usdt = float(client.balance("USDT")['free'])
        print(
            f"[{deal_exact_time}]  Sold coin {coin} at price {historical_data['prices'][index]} with RSI {historical_data['RSI'][index]}")
        order = Order(time=deal_exact_time, is_buy=False, coin=coin, price=historical_data['prices'][index],
                      usdt_price=gained_usdt, reason=algo_return.get_reason())
        return order


TRADING_SYMBOL = "MATICUSDT"
RECENT_INDEX = -1
TRADING_STEP_MINUTES = 20


def do_trading_round():
    usdt_balance = float(client.balance("USDT")["free"])
    historical_data = client.get_historical_data_on_interval(TRADING_SYMBOL, "1h", "3m")
    orders = orderDAO.get_orders()

    buy_order = check_and_buy(usdt_balance,
                              TRADING_SYMBOL,
                              historical_data,
                              RECENT_INDEX,
                              algorithms.algorithm.rsi_vwap_stop_loss,
                              orders)
    if buy_order is not None:
        orderDAO.put_order(buy_order)

    sell_order = check_and_sell(
        TRADING_SYMBOL,
        historical_data,
        RECENT_INDEX,
        algorithms.algorithm.rsi_vwap_stop_loss,
        orders)

    if sell_order is not None:
        orderDAO.put_order(sell_order)

    print(f"Trading round is completed.")


def do_trade():
    trading_counter = 0
    global trading_pause

    while True:
        if not trading_pause:
            print(f"Trading round: [{trading_counter}]")

            do_trading_round()

            print("Waiting for new trading round. Press key to finish")
            try:
                time.sleep(60 * TRADING_STEP_MINUTES)
            except KeyboardInterrupt:
                print("Loop interrupred")
                exit(0)
        else:
            # small timeout between checks
            time.sleep(1)

        trading_counter += 1


def is_started_trading():
    return is_thread_started


def start_trading():
    global is_thread_started
    is_thread_started = True
    thread = threading.Thread(target=do_trade)
    thread.daemon = True
    thread.start()


@app.route("/")
def root():
    if not is_started_trading():
        start_trading()

    usdt_balance = client.balance("USDT")
    coin_balance = client.balance(strutils.get_coin_out_of_symbol(TRADING_SYMBOL))

    order_history = orderDAO.get_orders()
    str = ""
    for order in order_history:
        str += f"<p>{order}</p>"
    return layout.page.body_top() + f"<h1> RSI trading bot - UP</h1>" \
                                    f"<h4>Balances: USDT: {usdt_balance}, coin: {coin_balance}</h4> " \
                                    f"{str}" + layout.page.body_bottom()


@app.route("/drop")
def flush():
    global trading_pause
    trading_pause = True
    try:
        db.drop_all_tables()
    except Exception as e:
        return f"<h1> Error during flushing data: {e}</h1>"
    finally:
        trading_pause = False
        return redirect(url_for("root"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5201))
    app.run(host='0.0.0.0', port=port)
