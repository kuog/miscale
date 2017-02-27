#!/usr/bin/env python

from gattlib import GATTRequester, GATTResponse
from binascii import hexlify
import time
import argparse
from miscale import *


parser = argparse.ArgumentParser(description='MI_SCALE requester')
parser.add_argument('-u','--user', help='user id', type=int, dest='user_id')
parser.add_argument('-d','--device', help='target MAC address', dest='device_mac')
args = parser.parse_args()

if args.user_id is None or args.device_mac is None:
	parser.print_help()
	exit(1)


def parse_user(user_id):
	"""
	Swap bytes order in user id
	"""
	return [x for x in struct.unpack("4B", struct.pack("<I", user_id))]


class MiRequester(GATTRequester):
	def on_notification(self, handle, data):
		print "[+] Notification on handle: %s" % hex(handle)
		val = hexlify(data).replace('1b2200', '')  # fix output formatting - remove operation code and handle
		print "\tPlain data: %s" % val
		parse_data(val, None)
		global get_measurements, close_session
		if val.find(USER_ID_STR) > -1:
			print "\t\tMeasurements count: %02d" % int(val[2:4], 16)
			get_measurements = 1
		elif val.find('03') > -1:
			close_session = 1

	def on_indication(self, handle, data):
		print "[+] Indication on handle: %s" % hex(handle)
		val = hexlify(data)
		print "\tPlain data: %s" % val

get_measurements = 0
close_session = 0
USER_DATA = parse_user(args.user_id)
USER_ID_STR = ''.join([hex(x) for x in USER_DATA]).replace('0x', '')


def pack_data(data):
	return str(bytearray(data))


def write_by_handle(data, handle, request):
	request.write_by_handle(handle, pack_data(data))


miscale_requester = MiRequester(args.device_mac)
write_by_handle([0x02, 0x00], 0x20, miscale_requester)  # unknown

print "[+] Unknown Data: %s" % hexlify(read_data(miscale_requester, CUSTOM_VALUE_UUID))
print "[+] Current Timestamp: %s" % parse_timestamp(hexlify(read_data(miscale_requester, CURRENT_TIMESTAMP_UUID)))

now = datetime.datetime.now()
current_stamp = struct.pack('<H', now.year)
current_stamp += pack_data([now.month, now.day, now.hour, now.minute, now.second, 0x06, 0x00, 0x00])
print "[*] Write Current Time %s (%s) ... " % (hexlify(current_stamp), now.strftime('%Y/%m/%d %H:%M:%S'))
miscale_requester.write_by_handle(0x1b, current_stamp)  # write timestamp

print "[+] Soft Revision: %s" % read_data(miscale_requester, SOFTWARE_REVISION_UUID)
print "[+] System Id: %s" % hexlify(read_data(miscale_requester, SYSTEM_ID_UUID))
print "[+] Serial Number: %s" % read_data(miscale_requester, SERIAL_NUMBER_UUID)
print "[+] PNP ID: %s" % hexlify(read_data(miscale_requester, PNP_ID_UUID))

write_by_handle([0x01, 0x00], 0x32, miscale_requester)
write_by_handle([0x01, 0x00], 0x23, miscale_requester)
print "[*] Write user id ..."
USER_DATA.insert(0, 0x01)
write_by_handle(USER_DATA, 0x22, miscale_requester)  # write user data
del USER_DATA[0]

print "[*] Wait for user data ..."
while get_measurements == 0:
	time.sleep(0.1)

write_by_handle([0x00, 0x00], 0x23, miscale_requester)
write_by_handle([0x01, 0x00], 0x23, miscale_requester)
write_by_handle([0x02], 0x22, miscale_requester)

print "[*] Wait for close ..."
while close_session == 0:
	time.sleep(0.1)

print "[*] Close session ..."
write_by_handle([0x03], 0x22, miscale_requester)
USER_DATA.insert(0, 0x04)
write_by_handle(USER_DATA, 0x22, miscale_requester)
del USER_DATA[0]
write_by_handle([0x00, 0x00], 0x23, miscale_requester)
