import threading
import time
import pandas as pd
from flask import Flask, redirect, url_for
import binance_wrapper
import layout
import os
import layout.page
import binance_simulator
import utils.stringutils as strutils

__name__ = "__main__"


binance = binance_wrapper.Client()
app = Flask(__name__)

is_thread_started = False
trading_pause = False


# client = binance_wrapper.Client()
client = binance_simulator.ClientMock()

symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "SOLUSDT", "AVAXUSDT", "LUNAUSDT", "DOTUSDT",
           "DOGEUSDT", "SHIBUSDT", "MATICUSDT", "LTCUSDT", "ATOMUSDT", "LINKUSDT", "TRXUSDT", "NEARUSDT", "BCHUSDT",
           "ALGOUSDT", "FTTUSDT", "XLMUSDT", "FTMUSDT", "UNIUSDT", "HBARUSDT", "MANAUSDT", "ICPUSDT", "ETCUSDT",
           "AXSUSDT", "SANDUSDT", "EGLDUSDT", "KLAYUSDT", "VETUSDT", "FILUSDT", "THETAUSDT", "XTZUSDT", "XMRUSDT",
           "GRTUSDT", "HNTUSDT", "EOSUSDT", "CAKEUSDT", "GALAUSDT", "FLOWUSDT", "TFUELUSDT", "AAVEUSDT", "ONEUSDT",
           "NEOUSDT", "MKRUSDT", "QNTUSDT", "ENJUSDT", "XECUSDT"]

posframe = pd.DataFrame(symbols)
posframe.columns = ["Currency"]
posframe["position"] = 0
posframe["quantity"] = 0

posframe.to_csv("positioncheck", index=False)

pd.read_csv("positioncheck")


LIMIT = 100


def get_hourly_data(symbol):
    return binance.get_historical_data(symbol, "1h", limit=LIMIT)


# result = get_hourly_data("BTCUSDT")
#
#
# # rsa = RelativeStrengthIndex(result["prices"])
# # rsa.calculate()
#
#
# for i in range(0, LIMIT):
#     print(str(result['prices'][i]) + " " + str(result['dates'][i]) + " " + str(result["RSI"][i]))


def changepos(curr, order, buy=True):
    if buy:
        posframe.loc[posframe.Currency == curr, 'position'] = 1
        posframe.loc[posframe.Currency == curr, 'quantity'] = float(order['executedQty'])

    else:
        posframe.loc[posframe.Currency == curr, 'position'] = 0
        posframe.loc[posframe.Currency == curr, 'quantity'] = 0


def trader(investment=100):
    print("SIMULATED BALANCES: " + str(client.get_balances_simulated_from_db()))

    for coin in posframe[posframe.position == 1].Currency:
        print(f"Check availability {coin} for SELL trade")
        hourly_data = get_hourly_data(coin)
        last_rsi = hourly_data["RSI"][-1]
        last_closing_price = hourly_data["prices"][-1]

        if last_rsi > 70:
            closing_price = last_closing_price
            selling_qty = posframe[posframe.Currency == coin].quantity.values[0]

            order = client.place_sell_order(symbol=coin,
                                            qty=selling_qty,
                                            price=closing_price)
            changepos(coin, order, buy=False)
            print(f"SOLD {order['executedQty']} of coin [{coin}]")

    for coin in posframe[posframe.position == 0].Currency:
        hourly_data = get_hourly_data(coin)
        last_rsi = hourly_data["RSI"][-1]
        last_closing_price = hourly_data["prices"][-1]

        if last_rsi < 30:
            buy_price = last_closing_price

            order = client.place_buy_order(symbol=coin,
                                           usdt_qty=investment,
                                           price=buy_price)

            if order['executedQty'] != 0:
                changepos(coin, order, buy=True)
                print(f"BOUGHT {order['executedQty']} of coin [{coin}]")

        else:
            print(f"Buying condition is not fulfilled for coin: {coin}")


def sell_everything():
    for coin in posframe[posframe.position == 1].Currency:
        df = get_hourly_data(coin)

        lastrow = df.iloc[-1]
        closing_price = lastrow.Close
        selling_qty = posframe[posframe.Currency == coin].quantity.values[0]

        order = client.place_sell_order(symbol=coin,
                                        qty=selling_qty,
                                        price=closing_price)

    return client.get_balances_simulated()


def emulate_sell_everything():
    emulated_usdt_balance = 0.0

    balances = client.get_balances_simulated_from_db()

    for balance in balances:
        if balance.currency == "USDT":
            emulated_usdt_balance += balance.amount
        else:
            symbol = strutils.get_binance_symbol_out_of_coin(balance.currency)
            currency_data = get_hourly_data(symbol)

            closing_price = currency_data["prices"][-1]

            order = client.emulate_place_sell_order(symbol=symbol,
                                                    qty=balance.amount,
                                                    price=closing_price)

            order_price_in_usdt = order['executedQty']
            emulated_usdt_balance += order_price_in_usdt

    return emulated_usdt_balance


def do_trade():
    trading_counter = 0
    global trading_pause

    while True:
        if not trading_pause:
            print(f"Trading round: [{trading_counter}]")
            trader(100)
            print("Waiting for new trading round. Press key to finish")
            try:
                time.sleep(60)
            except KeyboardInterrupt:
                print("Loop interrupred, selling everything")
                final_balance = sell_everything()
                print("-----------------SOLD EVERYTHING----------------")
                print("----------------SEE FINAL BAlANCE----------------")
                print(final_balance)
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

    balances = client.get_balances_simulated_from_db()
    calculated_current_usdt_balance = emulate_sell_everything()

    order_history = client.get_order_history()

    order_history_str = ""

    for order in order_history:
        order_history_str += "<p>" + repr(order) + "      ------       " + \
                             f'<a target="blank" href="https://www.binance.com/uk-UA/trade/{order.coin}_USDT" >' \
                             + order.coin + '</a>' + "<p/>\n"

    return layout.page.body_top() + f"<h1> RSI trading bot - UP</h1>" \
                                    f"<h4>DB balances {balances}</h4> " \
                                    f"<h4>Simulated USDT balance is {calculated_current_usdt_balance}</h4>" \
                                    f"<p>{order_history_str}<p>" + layout.page.body_bottom()


#
#
@app.route("/flush")
def flush():
    global trading_pause
    trading_pause = True
    try:
        client.flush()
    except Exception as e:
        return f"<h1> Error during flushing data: {e}</h1>"
    finally:
        trading_pause = False
        return redirect(url_for("root"))


# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 5201))
#     app.run(host='0.0.0.0', port=port)
#