import struct
import datetime
from binascii import unhexlify
from termcolor import colored

CUSTOM_VALUE_UUID = "00001542-0000-3512-2118-0009af100700"
NAME_UUID = "00002a00-0000-1000-8000-00805f9b34fb"
SERIAL_NUMBER_UUID = "00002a25-0000-1000-8000-00805f9b34fb"
SOFTWARE_REVISION_UUID = "00002a28-0000-1000-8000-00805f9b34fb"
SYSTEM_ID_UUID = "00002a23-0000-1000-8000-00805f9b34fb"
PNP_ID_UUID = "00002a50-0000-1000-8000-00805f9b34fb"
CURRENT_TIMESTAMP_UUID = "00002a2b-0000-1000-8000-00805f9b34fb"

WEIGHTSTAMP_LENGTH = 20
YEAR_END = 4
MONTH_END = YEAR_END + 2
DAY_END = MONTH_END + 2
HOUR_END = DAY_END + 2
MINUTE_END = HOUR_END + 2
SECOND_END = MINUTE_END + 2


def parse_data(operation_value, color):
	"""
	Parse multiple weightstamps from device like WEIGHTSTAMP1WEIGHTSTAMP2WEIGHTSTAMP3, etc.
	:param operation_value:
	:param color:
	:return:
	"""
	if len(operation_value) / WEIGHTSTAMP_LENGTH > 0 and len(operation_value) % WEIGHTSTAMP_LENGTH == 0:
		while len(operation_value) > 0:
			weight_stamp = operation_value[0:WEIGHTSTAMP_LENGTH]
			weight, date_str = parse_weightstamp(weight_stamp)
			if color is not None:
				print colored("\t\tWeight: %.2f, Timestamp: %s" % (weight, date_str), color)
			else:
				print "\t\tWeight: %.2f, Timestamp: %s" % (weight, date_str)
			operation_value = operation_value[WEIGHTSTAMP_LENGTH:]


def read_data(requester, uuid):
	"""
	Read bytes from device service
	:param requester: GATT requester
	:param uuid: Service UUID
	:return: bytes array
	"""
	return requester.read_by_uuid(uuid)[0]


def parse_timestamp(timestamp):
	"""
	Parse device timestamp like 'e0070c12003a31000000' to readable string like '2016/12/18 00:58:49'
	YY:YY   MM      DD      hh      mm      ss      ?
	Year    Month   Day     Hours   Minutes Second  ?
	e007    0c      12      00      3a      31      000000
	2016    12      18      00      58      49
	:param timestamp: timestamp converted as a byte string
	:return formatted date time string
	"""
	year = struct.unpack('<H', unhexlify(timestamp[0:YEAR_END]))[0]
	month = int(timestamp[YEAR_END:MONTH_END], 16)
	day = int(timestamp[MONTH_END:DAY_END], 16)
	hour = int(timestamp[DAY_END:HOUR_END], 16)
	minute = int(timestamp[HOUR_END:MINUTE_END], 16)
	second = int(timestamp[MINUTE_END:SECOND_END], 16)
	timestamp = datetime.datetime(year, month, day, hour, minute, second)
	return timestamp.strftime('%Y/%m/%d %H:%M:%S')


def parse_weightstamp(weightstamp):
	"""
	https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.characteristic.weight_measurement.xml
	Parse 2 bytes of weight
	XX:     WW:WW:  TT:TT:TT:TT:TT:TT:TT
	Flags   Weight  Timestamp
	:param weightstamp:
		Unit is in kilograms with a resolution of 0.005, and determined when bit 0 of the Flags field is set to 0.
		Unit:
		org.bluetooth.unit.mass.kilogram
		Exponent: Decimal, -3
		Multiplier: 5
	:return:
	"""
	if len(weightstamp) == WEIGHTSTAMP_LENGTH:
		weight = float((struct.unpack('<H', unhexlify(weightstamp[2:6])))[0] * 5) / 1000
		return weight, parse_timestamp(weightstamp[6:])
