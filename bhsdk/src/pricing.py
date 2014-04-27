#pricing models

from datetime import date
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
def getPremium(rate, d, amount, product_id) :
    now = date.today()
    n = (d - now).days
    if (n <= 0): n = 1

    t = float(n) / 365
    drift = 1
    s = rate + n * drift
    k = rate
    r = 0
    v = 2.0

    c = 1
    if product_id == BTCUSD_PUT_SHORT:
        c = -1
    return amount * bsPrice(s,k,t,v,r,c) / rate

def calculate_payment(rate_expiry, rate_initial, amount, pid):
    if pid == BTCUSD_CALL_SHORT:
        if rate_expiry < rate_initial:
            return amount * (rate_initial/rate_expiry -1)
    elif pid == BTCUSD_PUT_SHORT:
        if rate_expiry > rate_initial:
            return amount * (1 - rate_initial/rate_expiry)
    return 0
