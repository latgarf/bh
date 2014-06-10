#pricing models

import calendar  # for converting datetime tuples to unix epoch
from datetime import datetime, date
from math import sqrt
from scipy import stats
import math
from bhsdk.enums import BTCUSD_CALL_SHORT, BTCUSD_PUT_SHORT

def bsPrice(s, k, t, v, r, cp):
    # cp = +1/-1 for call/put
    d1 = (math.log(s/k)+(r+0.5*math.pow(v,2))*t)/(v*math.sqrt(t))
    d2 = d1 - v*math.sqrt(t)
    bsprice = cp*s*stats.norm.cdf(cp*d1) - cp*k*math.exp(-r*t)*stats.norm.cdf(cp*d2)
    return bsprice
# d_or_i: 0 for decrease, 1 for increase


def getPremium(rate, expiry, amount, product_id):
    # print('Expiry = ', expiry, '\n')                # expiry =  2014-05-10 
    # print('Expiry Type = ', type(expiry), '\n')     # type(expiry) =  <class 'datetime.date'> 

    expiry_epoch = calendar.timegm(expiry.timetuple())
    # print('expiry_epoch = ', expiry_epoch, '\n')    # expiry_epoch = 1399680000  (2014-05-10 00:00 UTC)
    # print('type(expiry_epoch) = ', type(expiry_epoch), '\n')  # type(expiry_epoch) =  <class 'int'> 
    
    now_epoch_tuple = datetime.utcnow()
    now_epoch = calendar.timegm(now_epoch_tuple.utctimetuple())
    time_to_expiry = expiry_epoch - now_epoch  # in seconds
    # print('time_to_expiry_epoch = ', time_to_expiry_epoch, '\n')
    
    t = time_to_expiry / 31536000   # 365 * 24 * 3600 = 31536000  seconds in a year
    drift = 1
    s = rate   # originally:  s = rate + n * drift
    k = rate
    r = 0
    v = 2.0

    c = 1
    if product_id == BTCUSD_PUT_SHORT:
        c = -1
    return amount * bsPrice(s,k,t,v,r,c) / rate



#~ def getPremium(rate, d, amount, product_id):
    #~ now_time = datetime.utcnow()
    #~ now_epoch = calendar.timegm(now_time.utctimetuple())
    #~ # now = date.today()
    #~ # n = (d - now).days
    #~ # if (n <= 0): n = 1
#~ 
    #~ time_to_expiry = expiry_epoch - now_epoch
    #~ 
    #~ t = time_to_expiry
    #~ drift = 1
    #~ s = rate + n * drift
    #~ k = rate
    #~ r = 0
    #~ v = 2.0
#~ 
    #~ c = 1
    #~ if product_id == BTCUSD_PUT_SHORT:
        #~ c = -1
    #~ return amount * bsPrice(s,k,t,v,r,c) / rate

'''
> import datetime
> datetime.datetime.now()
datetime.datetime(2013, 5, 11, 19, 47, 25, 375511)
'''



def calculate_payment(rate_expiry, rate_initial, amount, pid):
    if pid == BTCUSD_CALL_SHORT:
        if rate_expiry < rate_initial:
            return amount * (rate_initial/rate_expiry -1)
    elif pid == BTCUSD_PUT_SHORT:
        if rate_expiry > rate_initial:
            return amount * (1 - rate_initial/rate_expiry)
    return 0
