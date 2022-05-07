import numpy as np

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


MAX_INTERVAL_OVER_2_OVERSOLDS_H = 24 * 10
STOP_LOSS_THRESHOLD_PERCENT = 3
SAFE_EXIT_GAIN_PERCENT = 7


def __is_stop_loss_condition(historical_data, index, last_order):
    buying_price = last_order.price
    current_price = historical_data["prices"][index]
    condition_fulfilled = (buying_price / current_price - 1) * 100 > STOP_LOSS_THRESHOLD_PERCENT
    if condition_fulfilled:
        print(f"Condition STOP_LOSS fulfilled: {condition_fulfilled}")
    return condition_fulfilled


def __is_save_exit_condition(historical_data, index, last_order):
    buying_price = last_order.price
    current_price = historical_data["prices"][index]
    condition_fulfilled = (current_price / buying_price - 1) * 100 > SAFE_EXIT_GAIN_PERCENT
    print(f"{historical_data['dates'][index]} - Condition SAFE_EXIT fulfilled: {condition_fulfilled}")
    return condition_fulfilled

def is_price_forming_uptrend(historical_data, index, ma_interval):
    checking_interval = historical_data['prices'][index - 3: index + 1]
    is_forming_uptrend = np.all(np.diff(moving_average(np.array(checking_interval), n=ma_interval)) > 0)
    print(f"{historical_data['dates'][index]} - is forming uptrend = true")
    return is_forming_uptrend

def moving_average(a, n=3) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


def rsi_divergence(historical_data, index, check_condition, **kwargs):
    if check_condition == "BUY":
        price_rise_compared_to_1h_ago = historical_data["prices"][index] > historical_data["prices"][index - 1]
        price_rise_compared_to_2h_ago = historical_data["prices"][index] > historical_data["prices"][index - 2]

        is_forming_uptrend = is_price_forming_uptrend(historical_data, index, ma_interval=4)

        if is_forming_uptrend:
            print(f"{historical_data['dates'][index]} - Price rising condition is met: true")
            index -= 3
            rsi_index = historical_data["RSI"][index]

            is_rsi_just_above_30 = 30 <= rsi_index < 45
            was_rsi_failing_1h_ago = historical_data["RSI"][index - 1] < 30
            was_rsi_failing_2h_ago = historical_data["RSI"][index - 2] < 30

            rsi_started_rising = is_rsi_just_above_30 and was_rsi_failing_1h_ago

            if rsi_started_rising:
                print(f"{historical_data['dates'][index]} - RSI started rising condition is met: true")
                first_interval = None
                secnd_interval = None
                is_divergence_exist = False

                secnd_interval = __find_second_rsi_interval(historical_data, index)
                print("_______________________________")
                print(f"Second interval at dates {historical_data['dates'][secnd_interval[0]]} - {historical_data['dates'][secnd_interval[1]]}")

                # plot.build_2plots(historical_data["dates"][0:index + 2], historical_data["prices"][0:index + 2], historical_data["dates"][0:index + 2], historical_data["RSI"][0:index + 2])
                arg = secnd_interval[0] - MAX_INTERVAL_OVER_2_OVERSOLDS_H
                if arg < 0:
                    arg = 0
                is_first_interval_exist = 30 > min(historical_data["RSI"][arg:secnd_interval[0]])

                if is_first_interval_exist:
                    print("First interval exists")
                    first_interval = __find_first_rsi_interval(historical_data, secnd_interval[0] - 1)
                    print(
                        f"First interval at dates {historical_data['dates'][first_interval[0]]} - {historical_data['dates'][first_interval[1]]}")
                else:
                    print("First interval is not found")
                    return False

                is_divergence_exist = __is_divergence_exist(historical_data, first_interval, secnd_interval)
                print("_______________________________")
                return is_divergence_exist
            else:
                print(f"{historical_data['dates'][index]} - RSI rising condition is met: false")
        else:
            print(f"{historical_data['dates'][index]} - Price rising condition is met: false")
            return False
    elif check_condition == "SELL":
        rsi_index = historical_data["RSI"][index]

        condition_sell = rsi_index >= 69
        condition_stop_loss = False
        condition_safe_exit = False

        orders = kwargs.get("orders")
        if len(orders) > 0 and orders[-1].is_buy:
            condition_stop_loss = __is_stop_loss_condition(historical_data, index, orders[-1])
            condition_safe_exit = __is_save_exit_condition(historical_data, index, orders[-1])

        return condition_sell or condition_stop_loss or condition_safe_exit


def __find_second_rsi_interval(historical_data, end_index):
    current_rsi = historical_data["RSI"][end_index]
    first_ind_of_below30 = end_index - 1
    ind = first_ind_of_below30
    temp_rsi = historical_data["RSI"][ind]
    while temp_rsi < 30:
        temp_rsi = historical_data["RSI"][ind]
        if temp_rsi > 30:
            break
        ind -= 1

    return [ind + 1, first_ind_of_below30]


def __find_first_rsi_interval(historical_data, end_index):
    current_rsi = historical_data["RSI"][end_index]
    while current_rsi > 30:
        end_index -= 1
        current_rsi = historical_data["RSI"][end_index]

    first_ind_of_below30 = end_index
    ind = first_ind_of_below30
    temp_rsi = historical_data["RSI"][ind]
    while temp_rsi < 30:
        temp_rsi = historical_data["RSI"][ind -1]
        if temp_rsi < 30:
            ind -= 1
    return [ind, first_ind_of_below30]


def __is_divergence_exist(historical_data, first_interval, second_interval):
    min_rsi_on_first_interval = None
    if first_interval[0] != first_interval[1]:
        min_rsi_on_first_interval = min(historical_data["RSI"][first_interval[0]:first_interval[1] + 1])
    else:
        min_rsi_on_first_interval = historical_data["RSI"][first_interval[0]]

    min_rsi_on_second_interval = None
    if second_interval[0] != second_interval[1]:
        min_rsi_on_second_interval = min(historical_data["RSI"][second_interval[0]:second_interval[1] + 1])
    else:
        min_rsi_on_second_interval = historical_data["RSI"][second_interval[0]]


    if min_rsi_on_first_interval < min_rsi_on_second_interval:
        print("First RSI condition is met, checking for second")
        first_interval_min_index = None
        for i in range(first_interval[0], first_interval[1] + 1):
            if historical_data["RSI"][i] == min_rsi_on_first_interval:
                first_interval_min_index = i

        second_interval_min_index = None
        for i in range(second_interval[0], second_interval[1] + 1):
            if historical_data["RSI"][i] == min_rsi_on_second_interval:
                second_interval_min_index = i

        is_first_rsi_lower_than_second = min_rsi_on_first_interval < min_rsi_on_second_interval
        is_first_price_higher_than_second = historical_data["prices"][first_interval_min_index] > \
                                            historical_data["prices"][second_interval_min_index]
        print(f"Second divergence condition is met : {is_first_price_higher_than_second}, prices: [{historical_data['prices'][first_interval_min_index]}], [{historical_data['prices'][second_interval_min_index]}]")
        return is_first_rsi_lower_than_second and is_first_price_higher_than_second
    else:
        print(f"First divergence condition is met: false, min RSI[1] ({min_rsi_on_first_interval} is not less than min RSI[2] {min_rsi_on_second_interval}")
        return False
