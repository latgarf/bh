#!/usr/bin/python3

import subprocess
import json
import re
import os
import configparser

# from exceptions import TypeError

# CONFIG_FILE = '/etc/bhsite/bh_bitcoind.conf'
# if not os.path.exists(CONFIG_FILE):
#     CONFIG_FILE = 'bh_bitcoind.conf'

# config = configparser.SafeConfigParser()
# config.read(CONFIG_FILE)

def _run_bitcoind(args):
    args[0] = 'bitcoind ' + args[0]
    p = subprocess.Popen(' '.join(args), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ret = p.wait()
    if ret == 0:
        return [ str(l) for l in p.stdout.readlines()]
    return []

def sendtoaddress(address, amount):
    if not isinstance(amount, float):
        raise TypeError('sent_to_address: amount must be float type')

    command = 'bitcoind sendtoaddress %s %f' % (address, amount)
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = []
    for o in p.stdout.readlines():
        output.append(o.decode('utf-8').strip())

    ret = p.wait()
    if ret == 0:
        # success, return value is transaction id
        # e.g. d5792ed45301917d4dd972b88837c20de8e1bf8156ef13d1d1705333bcb0b64d
        # TODO: log transaction id, amount, to_address
        return (ret, output[0])
    else:
        # {"code": 4, "message": "insufficient funds"}
        # TODO: log error message
        json_str = re.search('\{.*\}', output[0]).group(0)
        json_obj = json.loads(json_str)
        return (ret, json_obj['message'])

def getreceivedbyaddress(addr, minconf=1):
    """ Returns in float payment amount received by addr. """

    args= ['getreceivedbyaddress', addr, minconf]
    o = _run_bitcoind(args)
    if o:
        s = re.search('([\d.]+)', o[0])
        if s:
            return float(s.group(1))
    else:
        # TODO: logging.warning, run command failed
        pass

    return 0.0
