import math


def round_down(num, precision):
    factor = 10.0 ** precision
    return math.floor(num * factor) / factor
