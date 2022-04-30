from numpy import ceil

import main2
import rsi_calculator
from utils import timestamp_utils as utils

ONE_HOUR_IN_MILLIS = 3_600_000

historical_data_1 = main2.get_historical_data(symbol="BTCUSDT", candle_interval="1h", limit=10000)

last_date = historical_data_1['dates'][0].timestamp()
last_date = utils.windows_to_standard_timestamp(last_date)
last_date_minus_hour = last_date - ONE_HOUR_IN_MILLIS


# 8640 hours in a year


def get_historical_data(symbol, candle_interval, limit):
    MAX_RECORDS_PER_TIME = 1000
    calling_times = int(ceil(limit / MAX_RECORDS_PER_TIME))

    calling_limit = MAX_RECORDS_PER_TIME if limit > MAX_RECORDS_PER_TIME else limit

    historical_data = main2.get_historical_data(symbol=symbol, candle_interval=candle_interval, limit=calling_limit)
    last_date_timestamp = utils.windows_to_standard_timestamp(historical_data["dates"][0].timestamp())
    print("Getting historical data.. part 1")
    last_date_minus_hour = last_date_timestamp - ONE_HOUR_IN_MILLIS

    for i in range(1, calling_times):
        print(f"Getting historical data.. part {i + 1}")

        temp = main2.get_historical_data(symbol=symbol, candle_interval=candle_interval, limit=calling_limit,
                                         endTime=last_date_minus_hour)
        last_date_timestamp = utils.windows_to_standard_timestamp(historical_data["dates"][0].timestamp())
        last_date_minus_hour = last_date_timestamp - ONE_HOUR_IN_MILLIS

        temp['prices'].extend(historical_data['prices'])
        temp['dates'].extend(historical_data['dates'])

        historical_data['prices'] = temp['prices']
        historical_data['dates'] = temp['dates']
        historical_data['RSI'] = rsi_calculator.calculate_rsi(historical_data["prices"])

    print("Done")
    return historical_data


historical_data = get_historical_data(symbol="BTCUSDT", candle_interval="1h", limit=3000)
print("Building plot")


# plot.build_plot(historical_data['dates'], historical_data['prices'])
# plot.build_2plots(historical_data['dates'], historical_data['prices'], historical_data['dates'], historical_data['RSI'])

def backtest_algo(algorithm, historical_data, starting_balance, currency):
    pass
# foreach hour
# for each currency
# if buy signal and sufficient balance
# then buy and change balance
# else if sell signal and have what to sell
# then sell everything and change usdt balance
