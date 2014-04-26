
class TransactionStatus:
    MIN = 0
    WAIT_FOR_PAYMENT = 0
    PAYMENT_RECEIVED_FULL = 1
    PAYMENT_RECEIVED_PARTIAL = 2
    CANCELLED = 3
    CLOSED = 4
    MAX = 4

VERBAL_STATUS = [
    'Waiting for payment',
    'Payment received - full',
    'payment received - partial',
    'Order cancelled'
    ]

def get_verbal_status(status):
    return VERBAL_STATUS[status]
