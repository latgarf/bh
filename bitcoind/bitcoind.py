#!/usr/bin/python3

import subprocess
import json
import re
from bitcoind_commands import *

BITCOIND = 'bitcoind'
TEST_ADDRESS = '1NtcLSUJhjVfQ7YdUU8GCwztAtDBFRXShh' # blockchain.info

def get_receive_command(from_address, minconf=1):
    return 'bitcoind getreceivedbyaddress %s %d' % (from_address, minconf)

# bitcoind sendtoaddress <toaddress> <amount>
def test_sendto():
    to_address = TEST_ADDRESS
    amount = 0.01
    send_to_address(TEST_ADDRESS, amount)

# bitcoind getreceivedbyaddress <fromaddress> [minconf=1]
def test_receive():
    from_address = TEST_ADDRESS
    p = subprocess.Popen(get_receive_command(from_address), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    retval = p.wait()
    if retval != 0:
        print('Error code:', retval)
        return
    print('total amount:', p.stdout.readlines())

def test_getbalance():

    p = subprocess.Popen('bitcoind getbalance', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    lines = p.stdout.readlines()
    print ('getbalance, number of lines:', len(lines))
    if len(lines) != 1:
        return

    print ('confirmed money', float(lines[0]))
    retval = p.wait()
    print ('return code:', retval)

if __name__ == "__main__":
    # test_getbalance()
    print ('=======================')
    test_sendto()
    print ('=======================')
    test_receive()