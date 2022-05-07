import datetime

from dateutil.relativedelta import relativedelta
from numpy import ceil

import binance
import config
import utils.timestamp_utils as utils
from utils import rsi_calculator, vwap_calculator

ONE_HOUR_IN_MILLIS = 3_600_000
MAX_RECORDS_PER_TIME = 720


class Client:

    def __init__(self):
        self.api_key = config.api_key
        self.secret_key = config.secret_key
        self.binance = binance.client.Client(self.api_key, self.secret_key)

    def balances(self):
        return binance.balances()

    def klines(self, pair, time_step, limit, **kwargs):
        return self.binance.get_klines(symbol=pair, interval=time_step, limit=limit, **kwargs)

    def place_buy_order(self, symbol, qty, price):
        return binance.order(symbol=symbol, side="BUY", orderType="MARKET", quantity=qty, price=price)

    def place_sell_order(self, symbol, qty, price):
        return binance.order(symbol=symbol, side="SELL", orderType="MARKET", quantity=qty, price=price)

    def __get_hour_limit_out_of_interval__(self, interval: str):
        if "y" in interval:
            number = int(interval.replace("y", ""))
            now = datetime.datetime.now()
            year_ago = now - relativedelta(years=number)
            delta = now - year_ago
            total_hours = delta.total_seconds() / 3600
            return total_hours

        if "m" in interval:
            number = int(interval.replace("m", ""))
            now = datetime.datetime.now()
            year_ago = now - relativedelta(months=number)
            delta = now - year_ago
            total_hours = delta.total_seconds() / 3600
            return int(total_hours)

    def get_historical_data_on_interval(self, symbol, candle_interval, interval):
        limit = self.__get_hour_limit_out_of_interval__(interval)

        calling_times = int(ceil(limit / MAX_RECORDS_PER_TIME))

        calling_limit = MAX_RECORDS_PER_TIME if limit > MAX_RECORDS_PER_TIME else limit

        historical_data = self.get_historical_data(symbol=symbol, candle_interval=candle_interval, limit=calling_limit)
        last_date_timestamp = utils.windows_to_standard_timestamp(historical_data["dates"][0].timestamp())
        print("Getting historical data.. part 1")
        last_date_minus_hour = last_date_timestamp - ONE_HOUR_IN_MILLIS

        for i in range(1, calling_times):
            print(f"Getting historical data.. part {i + 1}")
            temp = self.get_historical_data(symbol=symbol, candle_interval=candle_interval, limit=calling_limit,
                                            endTime=last_date_minus_hour)
            last_date_timestamp = utils.windows_to_standard_timestamp(temp["dates"][0].timestamp())
            last_date_minus_hour = last_date_timestamp - ONE_HOUR_IN_MILLIS

            temp['prices'].extend(historical_data['prices'])
            temp['highs'].extend(historical_data['highs'])
            temp['lows'].extend(historical_data['lows'])
            temp['volumes'].extend(historical_data['volumes'])
            temp['dates'].extend(historical_data['dates'])

            historical_data['prices'] = temp['prices']
            historical_data['highs'] = temp['highs']
            historical_data['lows'] = temp['lows']
            historical_data['volumes'] = temp['volumes']
            historical_data['dates'] = temp['dates']
        historical_data['RSI'] = rsi_calculator.calculate_rsi(historical_data["prices"])
        historical_data["VWAP"] = vwap_calculator.calculate_vwap(historical_data)
        historical_data["RSI-VWAP"] = rsi_calculator.calculate_rsi(historical_data['VWAP'])
        print("Done")
        return historical_data

    # 1499040000000,  # Open time
    # "0.01634790",  # Open
    # "0.80000000",  # High
    # "0.01575800",  # Low
    # "0.01577100",  # Close
    # "148976.11427815",  # Volume
    # 1499644799999,  # Close time
    # "2434.19055334",  # Quote asset volume
    # 308,  # Number of trades
    # "1756.87402397",  # Taker buy base asset volume
    # "28.46694368",  # Taker buy quote asset volume
    # "17928899.62484339"  # Can be ignored
    def get_historical_data(self, symbol, candle_interval, limit, **kwargs):
        data = self.klines(symbol, candle_interval, limit=limit, **kwargs)
        result = {}
        closing_prices = []
        high_prices = []
        low_prices = []
        volumes = []
        dates = []

        for data_item in data:
            high_price = float(data_item[2])
            high_prices.append(high_price)

            low_price = float(data_item[3])
            low_prices.append(low_price)

            closing_price = float(data_item[4])
            closing_prices.append(closing_price)

            volume = float(data_item[5])
            volumes.append(volume)

            close_time = datetime.datetime.fromtimestamp(data_item[6] / 1000)
            dates.append(close_time)

        result["prices"] = closing_prices
        result["dates"] = dates
        result["lows"] = low_prices
        result["highs"] = high_prices
        result["volumes"] = high_prices

        return result
