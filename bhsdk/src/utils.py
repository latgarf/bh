from binascii import hexlify
import bhsdk.constants as const
import os

def gen_query_id():
    """ Generate query ID. """
    return hexlify(os.urandom(16)).decode('utf-8')

def float_equal(a, b):
    return (abs(a-b) < const.PRECISION)

def float_equal_0(a):
    return float_equal(a, 0.0)


if __name__ == "__main__":
    print(gen_query_id())
    print('-'*30)
    print('0.0 equals 0? ', float_equal_0(0.0))
    print('0.0000001 equals 0? ', float_equal_0(0.0000001))
