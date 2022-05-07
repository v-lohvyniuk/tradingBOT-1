PERIOD = 14


def calculate_vwap(historical_data, period=PERIOD):
    closing_prices = historical_data["prices"]
    high_prices = historical_data["highs"]
    low_prices = historical_data["lows"]
    volumes = historical_data["volumes"]

    vwap = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for index in range(period, len(closing_prices)):
        avg_price_by_volume = 0
        weighted_volume = 0
        ind = index
        while ind > index - period:
            close_price = closing_prices[ind]
            high_price = high_prices[ind]
            low_price = low_prices[ind]
            volume = volumes[ind]

            weighted_volume += volume
            avg_price_by_volume += (high_price + low_price + close_price) / 3 * volume
            ind -= 1

        vwap.append(avg_price_by_volume / weighted_volume)

    return vwap
