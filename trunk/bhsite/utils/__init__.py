#!/usr/bin/env python3

from http import client
# from datetime import date
# from math import sqrt
import os

# from scipy import stats
# import math
import datetime, time
import json
# from bhsdk.enums import BTCUSD_CALL_SHORT, BTCUSD_PUT_SHORT


def getAmount():
    return 0.1

# def bsPrice(s, k, t, v, r, cp):
#     # cp = +1/-1 for call/put
#     d1 = (math.log(s/k)+(r+0.5*math.pow(v,2))*t)/(v*math.sqrt(t))
#     d2 = d1 - v*math.sqrt(t)
#     bsprice = cp*s*stats.norm.cdf(cp*d1) - cp*k*math.exp(-r*t)*stats.norm.cdf(cp*d2)
#     return bsprice

# # d_or_i: 0 for decrease, 1 for increase
# def getPremium(rate, d, amount, product_id) :
#     now = date.today()
#     n = (d - now).days
#     if (n <= 0): n = 1

#     drift = 1
#     s = rate + n * drift
#     k = rate
#     r = 0
#     v = 0.2

#     c = 1
#     if product_id == BTCUSD_PUT_SHORT:
#         c = -1
#     return amount * bsPrice(s,k,n,v,r,c) / rate

def getExpiryTime(date):
    exp_time = datetime.datetime(date.year, date.month, date.day) + datetime.timedelta(hours=21)
    return exp_time

if __name__ == '__main__':
    price = getRate()
    print('current price is:', price)
    print('desc fee is ', getPremium(198.2, date.today(), 0.1, 0))
    print('incs fee is ', getPremium(198.2, date.today(), 0.1, 1))

def getIP(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
