def calculate_sma(historical_data, field="prices", period=50):
    prices = historical_data[field]

    sma_list = []
    for i in range(0, period):
        sma_list.append(0)

    for index in range(period, len(prices)):
        ind = index
        avg_price = 0
        while ind > index - period:
            avg_price += prices[ind]
            ind -= 1

        avg_price_by_period = avg_price / period
        sma_list.append(avg_price_by_period)

    return sma_list
