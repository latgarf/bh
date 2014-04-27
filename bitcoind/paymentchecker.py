#!/usr/bin/env python3

# import os
import sqlite3
import datetime, time
import argparse

from bitcoind_commands import getreceivedbyaddress

from bhsdk import config
from bhsdk.constants import PRECISION
from bhsdk.utils import float_equal_0
from bhsdk.enums import TransactionStatus as TS
from bhsdk.time import now_epoch, now_epoch_str
from bhsdk import logger_payments as logger

MINCONF = config.get('bitcoind_params', 'minconf')
conn = sqlite3.connect(config.get('sqlite3', 'db_file'))
STATUS_IDX = 8
UID_IDX = 9
ADDR_USR_IDX = 5
VCHAR_INDICES = [0,1,2,4,5,9,10,11]


# Add double quotes to those fields of type varchar
def _get_query_str(fields):
    for ind in VCHAR_INDICES:
        fields[ind] = '"' + str(fields[ind]) + '"'
    return ','.join([str(f) for f in fields])

# query db for address list
def get_address_dict():
    """ return dict with key uid, value (address, amount). """
    c = conn.cursor()
    submitted = config.get('sqlite3', 'submitted_table')
    # col = config.get('sqlite3', 'addr_our_col')
    query = "SELECT * FROM %s WHERE status=%d" % (submitted, TS.WAIT_FOR_PAYMENT)
    ret = {}
    for a in c.execute(query):
        ret[a[UID_IDX]] = list(a)
    return ret


def add_new_order(uid, fields):
    """ Open a new order. """
    try:
        # update status and add 3 null to fields
        fields[STATUS_IDX] = TS.OPEN
        fields.extend(['null', 'null', 'null'])
        query="INSERT INTO opened VALUES(%s)" % _get_query_str(fields)
        c = conn.cursor()
        c.execute(query)

        # update status
        update_status_query = 'UPDATE %s set status = %d where order_id=\'%s\'' % (config.get('sqlite3', 'submitted_table'), TS.OPEN, uid)
        c.execute(update_status_query)
        conn.commit()
        return True
    except:
        return False

# processes new orders
def process_new_orders(new_order_dict, dry_run):
    total=0
    for uid in new_order_dict.keys():
        received = new_order_dict[uid][-1]
        amount   = new_order_dict[uid][3]
        fee      = new_order_dict[uid][6]

        # TODO: what if user pays large amount
        amount = float(amount) * float(received) / float(fee)
        new_order_dict[uid].append(amount)

        # add time_opened
        new_order_dict[uid].insert(-2, now_epoch_str())

        if dry_run:
            print('uid %s, %s received, %f amount opened, status %s' %(uid, received, amount, '1'))
            continue
        if not add_new_order(uid, new_order_dict[uid]):
            logger.warning('Open new order %s with payment %f and amount %f failed' % (uid, received, amount))
        total +=1
    logger.info('%s: %d new orders opened' % (now_epoch_str(), total))

def check_payments(dry_run):

    order_dict = get_address_dict()
    new_order_dict = {}
    for uid in order_dict.keys():
        addr   = order_dict[uid][ADDR_USR_IDX]
        a = getreceivedbyaddress(addr, MINCONF)
        if float_equal_0(a):
            continue
        new_order_dict[uid] = order_dict[uid]
        new_order_dict[uid].append(a)

    if dry_run:
        print('About to process %d new orders' % len(new_order_dict))

    if len(new_order_dict) > 0:
        process_new_orders(new_order_dict, dry_run)


def check_expiry(dry_run, verbal):
    exp_seconds = int(config.get('orders', 'order_exp_seconds'))
    threshold = now_epoch() - exp_seconds
    table = config.get('sqlite3', 'submitted_table')
    c = conn.cursor()

    condition = " WHERE time_ordered < '%d' AND status=%d" % (threshold, TS.WAIT_FOR_PAYMENT)

    q = ("SELECT order_id FROM %s " + condition) % table
    cnt = 0
    for r in c.execute(q):
        cnt += 1
        if dry_run:
            if verbal:
                print('[DRY RUN] Order %s expired' % r[0])
        else:
            logger.info('Order %s expired' % r[0])

    if dry_run:
        print('[DRY RUN] %d: Total %d orders expired' % (now_epoch(), cnt))
        return

    query = ("UPDATE %s SET status=%d " + condition) % (table, TS.CANCELLED)
    c.execute(query)
    conn.commit()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry', action='store_true')
    parser.add_argument('--verbal', action='store_true')
    args = parser.parse_args()

    check_payments(args.dry)
    check_expiry(args.dry, args.verbal)

if __name__ == "__main__":
    main()
