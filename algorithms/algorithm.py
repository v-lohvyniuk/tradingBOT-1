def rsi_on_rise(historical_data, index, check_condition, **kwargs):
    if check_condition == "BUY":
        rsi_index = historical_data["RSI"][index]
        is_rsi_index_above_30 = 30 <= rsi_index < 40
        was_rsi_failing_1h_ago = historical_data["RSI"][index - 1] < 30
        was_rsi_failing_2h_ago = historical_data["RSI"][index - 2] < 30
        return is_rsi_index_above_30 and (was_rsi_failing_1h_ago or was_rsi_failing_2h_ago)
    elif check_condition == "SELL":
        rsi_index = historical_data["RSI"][index]
        return rsi_index >= 69


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


def rsi(historical_data, index, check_condition, **kwargs):
    if check_condition == "BUY":
        rsi_index = historical_data["RSI"][index]
        return rsi_index < 30
    elif check_condition == "SELL":
        rsi_index = historical_data["RSI"][index]
        return rsi_index > 70


MAX_INTERVAL_OVER_2_OVERSOLDS_H = 10


def rsi_divergence(historical_data, index, check_condition, **kwargs):
    if check_condition == "BUY":
        rsi_index = historical_data["RSI"][index]

        is_rsi_just_above_30 = 30 <= rsi_index < 35
        was_rsi_failing_1h_ago = historical_data["RSI"][index - 1] < 30
        was_rsi_failing_2h_ago = historical_data["RSI"][index - 2] < 30

        rsi_started_rising = is_rsi_just_above_30 and (was_rsi_failing_1h_ago or was_rsi_failing_2h_ago)

        if rsi_started_rising:
            # get whole interval below 30
            end_index = index
            start_index = index
            for i in range(index, 0):
                if historical_data["RSI"][i] < 30:
                    i -= 1
                else:
                    start_index = i
                    break

            interval = {}
            interval["prices"] = historical_data["prices"][start_index:end_index + 1]
            interval["dates"] = historical_data["dates"][start_index:end_index + 1]
            interval["RSI"] = historical_data["RSI"][start_index:end_index + 1]

            min_rsi_index = interval["RSI"].index(min(interval["RSI"]))
            price_on_min_rsi = interval["prices"][min_rsi_index]

            # find_prev_below_30_interval

            start_interval_index = historical_data["dates"].index(interval["dates"][start_index])
            second_interval_end_index = -1
            for ind in range(start_interval_index - 1, start_interval_index - MAX_INTERVAL_OVER_2_OVERSOLDS_H):
                if historical_data["RSI"][ind] < 30:
                    second_interval_end_index = ind

            if second_interval_end_index == -1:
                return False
            else:
                second_interval_start_index = second_interval_end_index
                for i in range(second_interval_end_index, 0):
                    if historical_data["RSI"][i] < 30:
                        i -= 1
                    else:
                        second_interval_start_index = i
                        break


        current_price = historical_data["prices"][index]

        return None

    elif check_condition == "SELL":
        rsi_index = historical_data["RSI"][index]
        return rsi_index >= 69
