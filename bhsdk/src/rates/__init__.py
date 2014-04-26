from . import bitstamp


def get_rate():
    return bitstamp.get_24h_ma_rate()

def get_realtime_rate():
    return bitstamp.get_bitstamp_rate()

if __name__ == "__main__":
    print(get_rate())
