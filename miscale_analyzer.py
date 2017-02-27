#!/usr/bin/env python

import pyshark
import argparse
from miscale import *


HANDLE_VALUE_INDICATION = 0x1d
HANDLE_VALUE_NOTIFICATION = 0x1b
READ_RESPONSE = 0x0b
READ_REQUEST = 0x0a
WRITE_REQUEST = 0x12
CONNECT_REQ = 0x05

parser = argparse.ArgumentParser(description='BLE MI_SCALE protocol analyzer')
parser.add_argument('-u', '--user', help='user id', type=int, dest='user_id')
parser.add_argument('-c', '--capture', help='pcap file', dest='pcap_file')
args = parser.parse_args()


if args.user_id is None or args.pcap_file is None:
	parser.print_help()
	exit(1)



def parse_user(user_id):
	"""
	Repack user id into XX:XX:XX:XX formatted string
	"""
	user_bytes = [hex(x) for x in struct.unpack("4B", struct.pack("<I", user_id))]
	return ':'.join(user_bytes).replace('0x', '')

# user id bytes in XX:XX:XX:XX formatted string
USER_ID = parse_user(args.user_id)


def replace_user(data):
	"""
	Mask user id in output with "USER_ID" string
	:param data: BLE data to replace
	"""
	return data.replace(USER_ID, "USER_ID")


def get_ble_values(ble_packet):
	"""
	Parse BEL packet from pyshark format into variables
	:return:
		operation_handle: handle value as a hexadecimal string
		data: pyshark formatted byte string like xx:xx:xx:xx:xx:xx ...
		plain: plan data without ':' char
	"""
	operation_handle = ble_packet.btle.get_field_by_showname('Handle')
	data = ble_packet.btle.get_field_by_showname('Value')
	plain = data.replace(':', '')
	return operation_handle, data, plain


packets = pyshark.FileCapture(args.pcap_file)
for packet in packets:
	try:
		if int(packet.btle.type, 16) == CONNECT_REQ:
			print colored("[+] CONNECT_REQ", 'red')
			continue
	except AttributeError:  # There is no BLE header
		pass
	opcode = packet.btle.get_field_by_showname('Opcode')
	if opcode is not None:
		operation_type = int(opcode, 16)
		if operation_type == HANDLE_VALUE_INDICATION:
			# print indication parameters: handle and data
			handle, operation_data, plain_data = get_ble_values(packet)
			print colored("[+] Handle Value Indication:\n\tHandle: %s\n\tValue: %s" % (handle, operation_data), 'green')
			parse_data(plain_data, 'green')
		elif operation_type == READ_REQUEST:
			# print read request handle (the only one parameter)
			operation_data = packet.btle.get_field_by_showname('Handle')
			print colored("-> Read from handle: %s" % operation_data, 'magenta')
		elif operation_type == READ_RESPONSE:
			# print response parameters: handle and data
			handle, operation_data, plain_data = get_ble_values(packet)
			print colored("<- Read response: %s (%s)" % (operation_data, unhexlify(plain_data)), 'cyan')
			if operation_data.find('00:00:00') > -1:  # all read timestamps ends with 00:00:00 in pyshark format
				print colored("\t%s" % parse_timestamp(plain_data), 'cyan')
			if USER_ID in operation_data:
				print colored("\t%s" % replace_user(operation_data), 'cyan')
		elif operation_type == WRITE_REQUEST:
			# print write request parameters: handle and data to write
			handle, operation_data, plain_data = get_ble_values(packet)
			print colored("---> Write %s to %s" % (operation_data, handle), 'yellow')
			if handle == '0x001b': # handle for timestamp operations
				print colored("\t%s" % parse_timestamp(plain_data), 'yellow')
			if USER_ID in operation_data:
				print colored("\t%s" % replace_user(operation_data), 'yellow')
		elif operation_type == HANDLE_VALUE_NOTIFICATION:
			# print notification parameters: handle and data
			handle, operation_data, plain_data = get_ble_values(packet)
			print colored("[+] Handle Value Notification:\n\tHandle: %s\n\tValue: %s" % (handle, operation_data), 'green')
			parse_data(plain_data, 'green')
			if USER_ID in operation_data:
				print colored("\t%s" % replace_user(operation_data), 'green')
