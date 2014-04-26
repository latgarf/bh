#!/usr/bin/env python3

from bhsdk import config
from bhsdk import bitcoind
from bhsdk.time import now_epoch_str
from bhsdk.enums import TransactionStatus as TS
from bhsdk.pricing import calculate_payment
from bhsdk.rates import get_rate
from bhsdk import logger_payments as logger
import sqlite3
import json
import argparse

# def calculate_payment(rate_expiry, rate_initial, amount, pid):
#     if pid == BTCUSD_CALL_SHORT:
#         if rate_expiry < rate_initial:
#             return amount * (rate_initial/rate_expiry -1)
#     elif pid == BTCUSD_PUT_SHORT:
#         if rate_expiry > rate_initial:
#             return amount * (1 - rate_initial/rate_expiry)
#     return 0

def auto_pay(do_pay):
    """ return dict with key uid, value (address, amount). """

    min_payment = float(config.get('bitcoind_params', 'min_payment'))
    conn = sqlite3.connect(config.get('sqlite3', 'db_file'))
    c = conn.cursor()
    table = config.get('sqlite3', 'opened_table')

    query = ("SELECT product_id, order_id, addr_user, amount_opened, rate FROM %s "
             "WHERE time_expiry <= %s "
             "AND status=%d") % (table, now_epoch_str(), TS.OPEN)
    total = 0
    paid_count = 0
    bs = bitcoind.BitcoindService()
    for pid, uid, addr, amount, rate_i in c.execute(query):
        total +=1
        rate_exp = get_rate()
        amount_paid = calculate_payment(rate_exp, rate_i, amount, int(pid))
        print('amount is ', amount_paid)
        # Dry run
        if not do_pay:
            print('[DRY RUN]: pay %f to address %s, uid %s' % (amount_paid, addr, uid))
            continue

        (ret, trans_id, status) = (-1, 'None', TS.EXP_NO_PAYOUT_DUE)
        if amount_paid > 0:
            if amount_paid < min_payment:
                amount_paid = min_payment

            ret, trans_id = bs.sendtoaddress(addr, float(amount_paid))
            if ret == 0:
                logger.info('Paid to %s, amount %f, transaction ID: %s' % (addr, amount_paid, trans_id))
                status = TS.EXP_PAID_OUT
            else:
                logger.error('Payment failed: address %s, amount %f' % (addr, amount_paid))
                status = TS.EXP_PAYMENT_PENDING
        else:
            logger.info('Order %s expired without due payout' % uid)

        try:
            tp = now_epoch_str()
            update_cmd = ("UPDATE %s "
                          "SET time_closed=%s, "
                          "time_paid=%s, "
                          "payment_sent=%s, "
                          "status=%d "
                          "WHERE order_id='%s'") % (table, tp, tp, amount_paid, status, uid)
            c.execute(update_cmd)

            # save transaction id into transaction_ids table
            if ret == 0:
                trans_cmd = 'INSERT INTO %s VALUES(\'%s\', \'%s\')' % (config.get('sqlite3', 'transaction_ids_table'), uid, trans_id)
                c.execute(trans_cmd)
                paid_count +=1
            conn.commit()

        except Exception as e:
            conn.commit()
            logger.error(e)

    if do_pay:
        logger.info('%d processed, %d paid, %d expired worthless' % (total, paid_count, total-paid_count))


def main():
    parser = argparse.ArgumentParser(description='auto pay')
    parser.add_argument('--pay', action='store_true')
    args = parser.parse_args()
    auto_pay(args.pay)

if __name__ == "__main__":
    main()
