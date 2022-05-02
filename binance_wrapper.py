import datetime

from dateutil.relativedelta import relativedelta
from numpy import ceil

import binance
import config
import utils.timestamp_utils as utils
from utils import rsi_calculator

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
            temp['dates'].extend(historical_data['dates'])

            historical_data['prices'] = temp['prices']
            historical_data['dates'] = temp['dates']
            historical_data['RSI'] = rsi_calculator.calculate_rsi(historical_data["prices"])

        print("Done")
        return historical_data

    def get_historical_data(self, symbol, candle_interval, limit, **kwargs):
        data = self.klines(symbol, candle_interval, limit=limit, **kwargs)
        result = {}
        prices = []
        for data_item in data:
            closing_price = float(data_item[4])
            prices.append(closing_price)

        dates = []
        for data_item in data:
            close_time = datetime.datetime.fromtimestamp(data_item[6] / 1000)
            dates.append(close_time)

        result["prices"] = prices
        result["dates"] = dates
        result["RSI"] = rsi_calculator.calculate_rsi(result["prices"])

        return result
