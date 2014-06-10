
class TransactionStatus:
    MIN = 0
    WAIT_FOR_PAYMENT = 0
    CANCELLED = 1
    OPEN = 2
    EXP_NO_PAYOUT_DUE = 3
    EXP_PAYMENT_PENDING = 4
    EXP_PAID_OUT = 5
    MAX = 5

VERBAL_STATUS = [
    'Received - waiting for payment',
    'Cancelled - unpaid',
    'Open',
    'Expired - no insurance payout due.',
    'Expired - insurance payment pending.',
    'Expired - paid out.'
    ]

def get_verbal_status(status):
    return VERBAL_STATUS[status]

BTCUSD_CALL_SHORT = 1
BTCUSD_PUT_SHORT = 2

def prod_str(prod):
    return '%04d' % prod

INSURANCE_TYPES = [
    'DECREASE in bitcoin value vs USD',
    'INCREASE in bitcoin value vs USD'
    ]

def get_verbal_insurance_type(ins):
    return INSURANCE_TYPES[int(ins)-1]



