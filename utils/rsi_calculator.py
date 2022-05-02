PERIOD = 14


def calculate_rsi(prices_list: list, period=PERIOD):
    # step 1 - calculate upmoves and downmoves
    upmoves = []
    downmoves = []

    upmoves.append(0.0)
    downmoves.append(0.0)

    for i in range(1, len(prices_list)):
        prev_price = prices_list[i-1]
        current_price = prices_list[i]
        delta = prev_price - current_price
        if delta > 0:
            # 35 - 32 = 3    loss (down move)
            downmoves.append(delta)
            upmoves.append(0.0)
        else:
            # 32 - 35 = abs(3) - gain (up move)
            upmoves.append(abs(delta))
            downmoves.append(0.0)

    #step 2 - calculating averages (using Wilder's smoothing method https://www.macroption.com/rsi-calculation/ )
    # AvgUt = 1/14 * Ut + 13/14 * AvgUt-1

    upmoves_avg = []
    downmoves_avg = []

    upmoves_avg.append(1)
    downmoves_avg.append(1)

    for i in range(1, len(upmoves)):
        avg = 1/14 * upmoves[i] + 13/14 * upmoves_avg[i-1]
        upmoves_avg.append(avg)

    for i in range(1, len(downmoves)):
        avg = 1/14 * downmoves[i] + 13/14 * downmoves_avg[i-1]
        downmoves_avg.append(avg)

    # step 3 - calculate RS
    RS = []
    for i in range(0, len(upmoves_avg)):
        RS.append(upmoves_avg[i] / downmoves_avg[i])

    # step 4 - calculate RSI
    RSI = []

    for rs_item in RS:
        rsi_item = 100 - (100/(1 + rs_item))
        RSI.append(rsi_item)

    return RSI







