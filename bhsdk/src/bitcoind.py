#!/usr/bin/env python3

import json
import subprocess
import re
from bitcoinrpc.authproxy import AuthServiceProxy
from bhsdk import config

class BitcoindService():
    def __init__(self):
        # TODO: check if bitcoind server is running
        pass

    def _get_command_output_raw(self, command):
        import subprocess
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # ret = []
        # for l in p.stdout.readlines():
        #     ret.append(l)
        # return ret
        for o in p.stdout.readlines():
            yield o.decode('utf-8')

    def _get_command_output_json(self, command):
        import subprocess
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ret = p.wait()
        if ret != 0:
            # error occurs
            # TODO: raise exception, log error
            print('!!!! error occurs when calling %s' % command)
        out = p.communicate()[0]
        j_obj = json.loads(out.decode('utf-8'))

        return j_obj

    def validate_address(self, address):
        command = 'bitcoind validateaddress %s' % address
        ret = self._get_command_output_json(command)
        if 'isvalid' in ret:
            if ret['isvalid'] == True:
                return True
        return False

    def validate_address_rpc(self, address):
        rpc = AuthServiceProxy(config.get('bitcoind', 'connect'))
        return rpc.validateaddress(account)['isvalid']

    def get_new_address(self, account=''):
        command = 'bitcoind getnewaddress %s' % account
        li = self._get_command_output_raw(command)
        return next(li).strip()

    def get_new_address_rpc(self, account=''):
        rpc = AuthServiceProxy(config.get('bitcoind', 'connect'))
        return rpc.getnewaddress(account)

    def sendtoaddress(self, address, amount):
        # FIXME: temporarily solution
        command = 'bitcoind sendtoaddress %s %f' % (address, amount)
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = []
        for o in p.stdout.readlines():
            output.append(o.decode('utf-8').strip())

        ret = p.wait()
        if ret == 0:
            # success, return value is transaction id
            # e.g. d5792ed45301917d4dd972b88837c20de8e1bf8156ef13d1d1705333bcb0b64d
            # TODO: log transaction id, amount, to address
            return (ret, output[0])
        else:
            # {"code": 4, "message": "no sufficient funcs"}
            # TODO: log error message
            json_str = re.search('\{.*\}', output[0]).group(0)
            json_obj = json.loads(json_str)
            return (ret, json_obj['message'])

    def getreceivedbyaddress(addr, minconf=1):
        pass


if __name__ == "__main__":
    va = '19NSCG1oP38sJxzznpxHhx1v4bVggQPunp'
    iva = '19NSCG1oP38sJxzznpxHhx1v4b'
    bs = BitcoidService()
    # print(bs.validate_address(va))
    # print(bs.validate_address(iva))
    print('new address: ', bs.get_new_address())

