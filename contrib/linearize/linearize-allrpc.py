#!/usr/bin/env python3
#
# linearize-hashes.py:  List blocks in a linear, no-fork version of the chain.
#
# Copyright (c) 2013-2014 The Bitcoin Core developers
# Copyright (c) 2017 The Energi Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
#


try: # Python 3
    import http.client as httplib
except ImportError: # Python 2
    import httplib
import json
import re
import base64
try :
    import http.client as httplib
except ImportError:
    import httplib
import sys
import struct
from binascii import hexlify, unhexlify

settings = {}

##### Switch endian-ness #####
def hex_switchEndian(s):
	""" Switches the endianness of a hex string (in pairs of hex chars) """
	pairList = [s[i:i+2].encode() for i in range(0, len(s), 2)]
	return b''.join(pairList[::-1]).decode()

class BitcoinRPC:
	def __init__(self, host, port, username, password):
		authpair = "%s:%s" % (username, password)
		authpair = authpair.encode('utf-8')
		self.authhdr = b"Basic " + base64.b64encode(authpair)
		self.conn = httplib.HTTPConnection(host, port=port, timeout=30)

	def execute(self, obj):
		try:
			self.conn.request('POST', '/', json.dumps(obj),
				{ 'Authorization' : self.authhdr,
				  'Content-type' : 'application/json' })
		except ConnectionRefusedError:
			print('RPC connection refused. Check RPC settings and the server status.',
			      file=sys.stderr)
			return None

		resp = self.conn.getresponse()
		if resp is None:
			print("JSON-RPC: no response", file=sys.stderr)
			return None

		body = resp.read().decode('utf-8')
		resp_obj = json.loads(body)
		return resp_obj

	@staticmethod
	def build_request(idx, method, params):
		obj = { 'version' : '1.1',
			'method' : method,
			'id' : idx }
		if params is None:
			obj['params'] = []
		else:
			obj['params'] = params
		return obj

	@staticmethod
	def response_is_error(resp_obj):
		return 'error' in resp_obj and resp_obj['error'] is not None

def write_bootstrap_dat(settings, max_blocks_per_call=1000):
	outF = open(settings['output_file'], "wb")
	rpc = BitcoinRPC(settings['host'], settings['port'],
			 settings['rpcuser'], settings['rpcpassword'])

	height = settings['min_height']
	while height < settings['max_height']+1:
		num_blocks = min(settings['max_height']+1-height, max_blocks_per_call)
		batch = []
		for x in range(num_blocks):
			batch.append(rpc.build_request(x, 'getblockhash', [height + x]))

		reply = rpc.execute(batch)
		if reply is None:
			print('Cannot continue. Program will halt.')
			return None

		batch = []

		for x,resp_obj in enumerate(reply):
			if rpc.response_is_error(resp_obj):
				print('JSON-RPC: error at height', height+x, ': ', resp_obj['error'], file=sys.stderr)
				exit(1)
			assert(resp_obj['id'] == x) # assume replies are in-sequence
			hash = resp_obj['result']

			batch.append(rpc.build_request(x, 'getblock', [hash, False]))

		reply = rpc.execute(batch)
		if reply is None:
			print('Cannot continue. Program will halt.')
			return None

		for x,resp_obj in enumerate(reply):
			if rpc.response_is_error(resp_obj):
				print('JSON-RPC: error at height', height+x, ': ', resp_obj['error'], file=sys.stderr)
				exit(1)
			assert(resp_obj['id'] == x) # assume replies are in-sequence
			block = resp_obj['result']

			outF.write(settings['netmagic'])
			outF.write(struct.pack('<I', int(len(block) / 2)))
			outF.write(unhexlify(block.encode('ascii')))

		height += num_blocks
		print('At block height ', height)
		outF.flush()

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print("Usage: linearize-allrpc.py CONFIG-FILE")
		sys.exit(1)

	f = open(sys.argv[1])
	for line in f:
		# skip comment lines
		m = re.search('^\s*#', line)
		if m:
			continue

		# parse key=value lines
		m = re.search('^(\w+)\s*=\s*(\S.*)$', line)
		if m is None:
			continue
		settings[m.group(1)] = m.group(2)
	f.close()

	if 'host' not in settings:
		settings['host'] = '127.0.0.1'
	if 'port' not in settings:
		settings['port'] = 28843
	if 'min_height' not in settings:
		settings['min_height'] = 0
	if 'max_height' not in settings:
		settings['max_height'] = 1825000
	if 'rpcuser' not in settings or 'rpcpassword' not in settings:
		print("Missing username and/or password in cfg file", file=stderr)
		sys.exit(1)

	settings['port'] = int(settings['port'])
	settings['min_height'] = int(settings['min_height'])
	settings['max_height'] = int(settings['max_height'])

	settings['netmagic'] = unhexlify(settings['netmagic'].encode('ascii'))

	if 'output_file' not in settings:
		print("Missing output file")
		sys.exit(1)

	write_bootstrap_dat(settings)
