#!/usr/bin/env python3

from bhsdk import config
from http import client
import psycopg2
import json
import argparse


def get_sentinel_tid(conn, table):
    c = conn.cursor()
    i = c.execute("SELECT max(tid) FROM %s" % table)
    if i:
        for tid in i:
            if tid[0]:
               return int(tid[0])
    return -1

def fetch_history_to_db():
    parser = argparse.ArgumentParser()
    parser.add_argument('--day', action='store_true')
    parser.add_argument('--dry', action='store_true')
    args = parser.parse_args()

    conn = psycopg2.connect(config.get('db', 'connect'))
    t = config.get('db', 'bitstamp_history_table')

    domain=config.get('bitstamp', 'domain')
    trans_api = config.get('bitstamp', 'transaction_api')

    if args.day:
        trans_api = trans_api.replace('hour', 'day')

    # get sentinal from DB
    tid = get_sentinel_tid(conn, t)

    bs_conn = client.HTTPSConnection(domain, timeout=10)
    bs_conn.request('GET', trans_api)
    trans = json.loads(str(bs_conn.getresponse().read(), 'UTF-8'))

    c = conn.cursor()
    for tr in trans:
        if int(tr['tid'] <= tid):
            continue
        # insert into DB
        q = "INSERT INTO %s(ts, tid, price, amount) VALUES(%s, %s, %s, %s)" % (t, tr['date'], tr['tid'], tr['price'], tr['amount'])
        if args.dry:
            print(q)
            continue
        c.execute(q)
    conn.commit()

if __name__ == "__main__":
    fetch_history_to_db()
