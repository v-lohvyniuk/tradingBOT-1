def rsi_on_rise_enhanced(historical_data, index, check_condition, **kwargs):
    orders = kwargs.get("orders")

    if check_condition == "BUY":
        rsi_index = historical_data["RSI"][index]
        is_rsi_index_above_30 = 30 <= rsi_index < 40
        was_rsi_failing_1h_ago = historical_data["RSI"][index - 1] < 30
        was_rsi_failing_2h_ago = historical_data["RSI"][index - 2] < 30
        return is_rsi_index_above_30 and (was_rsi_failing_1h_ago or was_rsi_failing_2h_ago)
    elif check_condition == "SELL":
        if len(orders) == 0:
            return False
        else:
            rsi_index = historical_data["RSI"][index]
            current_price = historical_data["prices"][index]
            last_order_price = orders[-1].price
            last_order_type_is_buy = orders[-1].is_buy

            condition_1 = rsi_index >= 69
            # if raise is more than 10%
            condition_2 = last_order_type_is_buy and current_price / last_order_price >= 1.1

            return condition_1 or condition_2
