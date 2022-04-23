import time
import os
import pandas as pd
import threading
from flask import Flask, render_template

__name__ = "__main__"
app = Flask(__name__)

is_thread_started = False


import binance_simulator

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


print(client.get_balances())


def gethourlydata(symbol):
    frame = pd.DataFrame(client.klines(symbol, "1h", limit=75))

    frame = frame[["openTime", "close"]]
    frame.columns = ['Time', 'Close']
    frame.Close = frame.Close.astype(float)
    frame.Time = pd.to_datetime(frame.Time, unit='ms')

    return frame


temp = gethourlydata("BTCUSDT")


def applytechnicals(df):
    df["FastSMA"] = df.Close.rolling(7).mean()
    df["SlowSMA"] = df.Close.rolling(30).mean()


applytechnicals(temp)


def changepos(curr, order, buy=True):
    if buy:
        posframe.loc[posframe.Currency == curr, 'position'] = 1
        posframe.loc[posframe.Currency == curr, 'quantity'] = float(order['executedQty'])

    else:
        posframe.loc[posframe.Currency == curr, 'position'] = 0
        posframe.loc[posframe.Currency == curr, 'quantity'] = 0


def trader(investment=100):
    print("SIMULATED BALANCES: " + str(client.get_balances_simulated()))

    for coin in posframe[posframe.position == 1].Currency:
        print(f"Check availability {coin} for SELL trade")
        df = gethourlydata(coin)
        applytechnicals(df)
        lastrow = df.iloc[-1]
        if lastrow.SlowSMA > lastrow.FastSMA:
            # how to get the order price ???? probably this way
            closing_price = lastrow.Close
            selling_qty = posframe[posframe.Currency == coin].quantity.values[0]

            order = client.place_sell_order(symbol=coin,
                                            qty=selling_qty,
                                            price=closing_price)
            changepos(coin, order, buy=False)
            print(f"SOLD {order['executedQty']} of coin [{coin}]")

    for coin in posframe[posframe.position == 0].Currency:
        df = gethourlydata(coin)
        applytechnicals(df)
        lastrow = df.iloc[-1]
        is_higher = lastrow.FastSMA >= lastrow.SlowSMA
        is_just_became_higher = 1 - (lastrow.SlowSMA / lastrow.FastSMA) <=0.01
        if is_higher and is_just_became_higher:
            buy_price = lastrow.Close

            order = client.place_buy_order(symbol=coin,
                                           qty=investment,
                                           price=buy_price)

            if order['executedQty'] != 0:
                changepos(coin, order, buy=True)
                print(f"BOUGHT {order['executedQty']} of coin [{coin}]")

        else:
            print(f"Buying condition is not fulfilled for coin: {coin}")


def sell_everything():
    for coin in posframe[posframe.position == 1].Currency:
        df = gethourlydata(coin)
        applytechnicals(df)
        lastrow = df.iloc[-1]
        closing_price = lastrow.Close
        selling_qty = posframe[posframe.Currency == coin].quantity.values[0]

        order = client.place_sell_order(symbol=coin,
                                        qty=selling_qty,
                                        price=closing_price)

    return client.get_balances_simulated()


def emulate_sell_everything():
    emulated_usdt_balance = 0
    for coin in posframe[posframe.position == 1].Currency:
        df = gethourlydata(coin)
        applytechnicals(df)
        lastrow = df.iloc[-1]
        closing_price = lastrow.Close
        selling_qty = posframe[posframe.Currency == coin].quantity.values[0]

        order = client.emulate_place_sell_order(symbol=coin,
                                        qty=selling_qty,
                                        price=closing_price)

        order_price_in_usdt = order['executedQty']
        emulated_usdt_balance += order_price_in_usdt

    return emulated_usdt_balance


def do_trade():
    trading_counter = 0

    while True:
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
def hello():
    if not is_started_trading():
        start_trading()

    balances = client.get_balances_simulated()
    calculated_current_usdt_balance = emulate_sell_everything()

    order_history_str = ""
    for order in client.order_history:
        order_copy = order.copy()

        order_copy[2] = f'<a target="blank" href="https://www.binance.com/ru/trade/{order[2]}_USDT" >' + order[2] + '</a>'
        order_history_str += "<p>" + str(order_copy) + "" + "<p/>\n"

    return f"<h1> Application is UP, all services are running </h1>" \
           f"<h4>{balances}</h4> " \
           f"<h4>Simulated USDT balance is {calculated_current_usdt_balance}</h4>" \
           f"<h5>{order_history_str}<h5>"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5201))
    app.run(host='0.0.0.0', port=port)

