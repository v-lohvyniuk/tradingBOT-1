import os
import json


class AlgorithmConfiguration:

    def __init__(self):
        pass


class AlgoConfig:
    rsi_vwap_stop_loss = AlgorithmConfiguration()
    rsi_vwap_stop_loss.RSI_PEAK = 98
    rsi_vwap_stop_loss.RSI_PEAK_SMALL = 16
    rsi_vwap_stop_loss.RSI_BUY = 18
    rsi_vwap_stop_loss.STOP_LOSS_PERCENT = 0.9


api_key = "VDcO1lz9EvhDm35RwdQJEWxlW3vGnAkxRXhQyVTBv1CUxNiH3kTMBX7kqtLNxkuZ"
secret_key = "y17hJJxolUwIQNPAfDP98ouHiZzKToqQhPQHRqJ99B336MvyXelBhXi9txZOkCBb"

STARTING_BALANCE = 500.0
