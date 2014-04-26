from http import client
from bhsdk import config
from bhsdk.time import now_epoch
import bhsdk.constants as const
import json
import sqlite3
import numpy as np

# FIXME: use the one from config file
BS_DOMAIN = config.get('bitstamp', 'domain')
RATE_API = config.get('bitstamp', 'rate_api')

TABLE = config.get('sqlite3', 'bitstamp_history_table')

# Real time rate
def get_bitstamp_rate():
    try:
        con= client.HTTPSConnection(BS_DOMAIN, timeout=5)
        con.request('GET', RATE_API)
        j = json.loads(str(con.getresponse().read(), 'UTF-8'))
        return float(j['last'])
    except:
        # TODO : log warning and need plan B
        pass
    return const.BASE_USD_RATE

def get_24h_ma_rate():
    """ Volume weighted moving average price over last 24 hours. """

    try:
        CONN = sqlite3.connect(config.get('sqlite3', 'db_file'))
        prices = []
        amounts = []
        threshold = now_epoch() - 24*60*60
        q = "SELECT price, amount FROM %s WHERE ts > '%d'" % (TABLE, threshold)
        c = CONN.cursor()
        for p, a in c.execute(q):
            prices.append(p)
            amounts.append(a)
        if prices:
            return np.average(prices, weights=amounts)
    except:
        pass

    # If anything goes wrong, return realtime rate
    return get_bitstamp_rate()

if __name__ == "__main__":
    #get_bitstamp_history()
    # print(get_bitstamp_rate())
    print('24hr ma rate is ', get_24h_ma_rate())
