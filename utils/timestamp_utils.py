from numpy.compat import long


def windows_to_standard_timestamp(timestamp):
    if type(timestamp) is float:
        timestamp *= 1000
        return long(timestamp)
    else:
        print(f"timestamp {timestamp} is already in standard format")
        return timestamp