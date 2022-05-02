import binance_wrapper
from algorithms import algorithm
from backtest.data import BacktestResults
from db.client import Order
from plots import plot

binance = binance_wrapper.Client()


def backtest_algo(algorithm, historical_data, starting_balance=500, currency="BTCUSDT"):
    backtest_result = BacktestResults()

    balances = {"USDT": starting_balance}
    coin = currency.replace("USDT", "")

    size = len(historical_data['dates'])
    for index in range(0, size):
        order_buy = check_and_buy(balances, coin, historical_data, index, algorithm, backtest_result.orders)
        if order_buy is not None:
            backtest_result.add_buy_order(order_buy)

        order_sell = check_and_sell(balances, coin, historical_data, index, algorithm, backtest_result.orders)
        if order_sell is not None:
            backtest_result.add_sell_order(order_sell)

        historical_data["USDT"] = balances['USDT']
        if coin in balances.keys():
            historical_data[coin] = balances[coin]
        else:
            historical_data[coin] = 0.0

    print("Algorithm Simulation complete")

    # sell everything at the end
    print(f"Balances {balances}")
    print(f"Selling everything ... ")

    for curr, amount in balances.items():
        if curr != "USDT" and amount > 0.0:
            selling_price = historical_data["prices"][-1]
            usdt_gained = selling_price * amount
            balances["USDT"] += usdt_gained
            balances[coin] = 0.0
    print(f"Balances {balances}")

    print(f"Final USDT balance is {balances['USDT']}")

    backtest_result.set_final_usdt_result(balances['USDT'])

    return backtest_result


def check_and_buy(balances, coin, historical_data, index, algorithm, orders):
    is_able_to_buy = balances["USDT"] > 0.0

    if is_able_to_buy:
        should_buy = algorithm(historical_data, index, check_condition="BUY", orders=orders)
        if should_buy:
            spent_cost = balances["USDT"]
            bought_coin = spent_cost / historical_data["prices"][index]
            balances[coin] = bought_coin
            balances["USDT"] = 0.0
            deal_exact_time = historical_data['dates'][index]
            print(
                f"[{deal_exact_time}]  Bought coin {coin} at price {historical_data['prices'][index]} with RSI {historical_data['RSI'][index]}")
            order = Order(time=deal_exact_time, is_buy=True, coin=coin, price=historical_data['prices'][index],
                          usdt_price=spent_cost)
            return order


def check_and_sell(balances, coin, historical_data, index, algorithm, orders):
    should_sell = algorithm(historical_data, index, check_condition="SELL", orders=orders)

    if should_sell and coin in balances.keys() and balances[coin] > 0.0:
        coin_balance = balances[coin]
        gained_usdt = coin_balance * historical_data["prices"][index]
        balances["USDT"] += gained_usdt
        balances[coin] = 0.0
        deal_exact_time = historical_data['dates'][index]
        print(
            f"[{deal_exact_time}]  Sold coin {coin} at price {historical_data['prices'][index]} with RSI {historical_data['RSI'][index]}")
        order = Order(time=deal_exact_time, is_buy=False, coin=coin, price=historical_data['prices'][index],
                      usdt_price=gained_usdt)
        return order


# symbols_to_backtest = main2.symbols
symbols_to_backtest = ["LUNAUSDT"]

for symbol_to_backtest in symbols_to_backtest:
    historical_data = binance.get_historical_data(symbol=symbol_to_backtest, candle_interval="1h", limit=2000)

    backtest_result = backtest_algo(algorithm.rsi_on_rise_enhanced, historical_data, 500, symbol_to_backtest)

    plot.build_2plots_with_buy_sell_markers(historical_data['dates'], historical_data['prices'],
                                            historical_data['dates'], historical_data['RSI'],
                                            buy_markers=backtest_result.buy_points,
                                            sell_markers=backtest_result.sell_points)
