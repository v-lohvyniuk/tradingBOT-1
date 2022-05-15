import datetime

import binance_wrapper
from algorithms import algorithm
from backtest.data import BacktestResults
from db.client import Order
from plots import plot
import numpy
from config import AlgoConfig
from utils import files

binance = binance_wrapper.Client()


def backtest_algo(algorithm, historical_data, starting_balance=500, currency="BTCUSDT"):
    backtest_result = BacktestResults()
    backtest_result.coin = currency

    balances = {"USDT": starting_balance}
    coin = currency.replace("USDT", "")

    size = len(historical_data['dates'])
    indexes = []
    for index in range(0, size):
        order_buy = check_and_buy(balances, coin, historical_data, index, algorithm, backtest_result.orders)
        if order_buy is not None:
            backtest_result.add_buy_order(order_buy)
            indexes.append(index)

        order_sell = check_and_sell(balances, coin, historical_data, index, algorithm, backtest_result.orders)
        if order_sell is not None:
            backtest_result.add_sell_order(order_sell)
            indexes.append(index)

    print("Algorithm Simulation complete")

    print(f"Balances {balances}")

    # sell everything at the end
    print(f"Selling everything ... ")

    for curr, amount in balances.items():
        if curr != "USDT" and amount > 0.0:
            selling_price = historical_data["prices"][-1]
            usdt_gained = selling_price * amount
            balances["USDT"] += usdt_gained
            balances[coin] = 0.0
    print(f"Balances {balances}")

    backtest_result.set_final_usdt_result(balances['USDT'])

    return backtest_result


def check_and_buy(balances, coin, historical_data, index, algorithm, orders):
    is_able_to_buy = balances["USDT"] > 0.0

    if is_able_to_buy:
        algo_return = algorithm(historical_data, index, check_condition="BUY", orders=orders)
        should_buy = algo_return.should_buy()
        if should_buy:
            spent_cost = balances["USDT"]
            bought_coin = spent_cost / historical_data["prices"][index]
            balances[coin] = bought_coin
            balances["USDT"] = 0.0
            deal_exact_time = historical_data['dates'][index]
            # print(
            #     f"[{deal_exact_time}]  Bought coin {coin} at price {historical_data['prices'][index]} with RSI {historical_data['RSI'][index]}")
            order = Order(time=deal_exact_time, is_buy=True, coin=coin, price=historical_data['prices'][index],
                          usdt_price=spent_cost, reason=algo_return.get_reason())
            return order


def check_and_sell(balances, coin, historical_data, index, algorithm, orders):
    algo_return = algorithm(historical_data, index, check_condition="SELL", orders=orders)
    should_sell = algo_return.should_sell()

    if should_sell and coin in balances.keys() and balances[coin] > 0.0:
        coin_balance = balances[coin]
        gained_usdt = coin_balance * historical_data["prices"][index]
        balances["USDT"] += gained_usdt
        balances[coin] = 0.0
        deal_exact_time = historical_data['dates'][index]
        # print(
        #     f"[{deal_exact_time}]  Sold coin {coin} at price {historical_data['prices'][index]} with RSI {historical_data['RSI'][index]}")
        order = Order(time=deal_exact_time, is_buy=False, coin=coin, price=historical_data['prices'][index],
                      usdt_price=gained_usdt, reason=algo_return.get_reason())
        return order


# symbols_to_backtest = main2.symbols
# symbols_to_backtest = ["BTCUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT", "AVAXUSDT", "DOTUSDT", "LTCUSDT", "ALGOUSDT", "MATICUSDT", "BCHUSDT", "GALAUSDT"]
# symbols_to_backtest = ["DOGEUSDT", "ATOMUSDT", "LINKUSDT", "TRXUSDT", "MANAUSDT", "THETAUSDT", "CAKEUSDT"]
symbols_to_backtest = ["LUNAUSDT"]

sym = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT", "AVAXUSDT", "LUNAUSDT", "DOTUSDT",
       "DOGEUSDT", "SHIBUSDT", "MATICUSDT", "LTCUSDT", "ATOMUSDT", "LINKUSDT", "TRXUSDT", "NEARUSDT", "BCHUSDT",
       "ALGOUSDT", "FTTUSDT", "XLMUSDT", "FTMUSDT", "UNIUSDT", "HBARUSDT", "MANAUSDT", "ICPUSDT", "ETCUSDT",
       "AXSUSDT", "SANDUSDT", "EGLDUSDT", "KLAYUSDT", "VETUSDT", "FILUSDT", "THETAUSDT", "XTZUSDT", "XMRUSDT",
       "GRTUSDT", "HNTUSDT", "EOSUSDT", "CAKEUSDT", "GALAUSDT", "FLOWUSDT", "TFUELUSDT", "AAVEUSDT", "ONEUSDT",
       "NEOUSDT", "MKRUSDT", "QNTUSDT", "ENJUSDT", "XECUSDT"]

backtest_results = []

filename = files.get_dated_filename("rsi_vwap_stop_loss")
for symbol_to_backtest in symbols_to_backtest:
    try:
        historical_data = binance.get_historical_data_on_interval(symbol=symbol_to_backtest, candle_interval="1h",
                                                                  interval="1y")

        rsi_low_range = range(5, 30)
        rsi_peak_range = range(70, 100)
        rsi_small_peak_range = range(16, 40)

        results = []
        results_prices = []
        for rsi_low in rsi_low_range:
            for rsi_peak in rsi_peak_range:
                for rsi_small_peak in rsi_small_peak_range:
                    AlgoConfig.rsi_vwap_stop_loss.RSI_BUY = rsi_low
                    AlgoConfig.rsi_vwap_stop_loss.RSI_PEAK_SMALL = rsi_small_peak
                    AlgoConfig.rsi_vwap_stop_loss.RSI_PEAK = rsi_peak

                    backtest_result = backtest_algo(algorithm.rsi_vwap_stop_loss, historical_data, 500, symbol_to_backtest)

                    print("COIN: " + backtest_result.coin)
                    print("Final USDT balance: " + str(backtest_result.final_usdt))
                    print("Number of sales: " + str(len(backtest_result.orders) / 2))

                    results.append([
                        f"LOW: {rsi_low}, PEAK: {rsi_peak}, SMALL: {rsi_small_peak}. Final USDT: {backtest_result.final_usdt}",
                        backtest_result.final_usdt])
                    results_prices.append(backtest_result.final_usdt)
                    # plot.build_2plots_with_buy_sell_markers(
                    #     first_plot_data=
                    #     [
                    #         [historical_data['dates'], historical_data['prices']],
                    #         [historical_data['dates'], historical_data['MA-200']],
                    #         [historical_data['dates'], historical_data['MA-50']],
                    #         [historical_data['dates'], historical_data['MA-20']],
                    # ],
                    # second_plot_data=
                    # [[historical_data['dates'], historical_data['RSI-VWAP']]],
                    #
                    # buy_markers=backtest_result.buy_points,
                    # sell_markers=backtest_result.sell_points)

        files.create_file(filename)
        files.append_log(filename, symbol_to_backtest)

        max_gain = numpy.amax(numpy.array(results_prices))
        print(f"Max gain is {max_gain}")
        files.append_log(filename, f"Max gain is {max_gain}")
        for item in results:
            if item[1] == max_gain:
                print(item[0])
                files.append_log(filename, item[0])
    except Exception as e:
        print(e)

