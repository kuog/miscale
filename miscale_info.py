#!/usr/bin/env python
from gattlib import DiscoveryService, GATTRequester
from binascii import hexlify
import argparse
from miscale import *


parser = argparse.ArgumentParser(description='MI_SCALE base info')
parser.add_argument('-b', '--btaddr', help='target BTADDR in XX:XX:XX:XX:XX:XX format', dest='btaddr')
parser.add_argument('-d', '--device', help='hci device name (e.g. hci0)', default='hci0', dest='device')
parser.add_argument('-l', '--listen', help='listen to advertises', action='store_true', dest='is_info')
args = parser.parse_args()

if args.btaddr is None and args.is_info is False:
	print 'You should specify at least one argument.'
	parser.print_help()
	exit(1)
elif args.is_info:
	ble_discovery = DiscoveryService(args.device)
	devices = ble_discovery.discover(2)
	for device_address, device_name in devices.items():
		print("name: {}, address: {}".format(device_name, device_address))
else:
	gatt_requester = GATTRequester(args.btaddr)
	print "Device Name: %s" % read_data(gatt_requester, NAME_UUID)
	print "Device Serial Number: %s" % read_data(gatt_requester, SERIAL_NUMBER_UUID)
	print "Device Software Revision: %s" % read_data(gatt_requester, SOFTWARE_REVISION_UUID)
	print "Device System ID: %s" % hexlify(read_data(gatt_requester, SYSTEM_ID_UUID))
	print "Device PNP ID: %s" % hexlify(read_data(gatt_requester, PNP_ID_UUID))
	print "Device Current Timestamp: %s" % parse_timestamp(hexlify(read_data(gatt_requester, CURRENT_TIMESTAMP_UUID)))