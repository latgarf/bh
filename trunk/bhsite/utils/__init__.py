#!/usr/bin/env python3

from http import client
import os
import datetime, time
import json

def getAmount():
    return 0.1

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
