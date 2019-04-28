#!/usr/bin/python -B
# -*- coding: utf-8 -*-
import struct


def parse_unsigned_int(data, start, length):
	sbyte = int(start / 4)
	ebyte = int(sbyte + length / 4)

	# Extract field from string
	svalue = data[sbyte:ebyte]

	# Pair-wise reverse ascii bytes
	nvalue = "".join(reversed([svalue[i:i + 2] for i in range(0, len(svalue), 2)]))

	ivalue = int(nvalue, 16)

	return ivalue


def parse_signed_int(data, start, length):
	unsigned = parse_unsigned_int(data, start, length)

	packed = struct.pack('H', unsigned)
	signed_val = struct.unpack('h', packed)[0]

	return signed_val


class Msg_1a6(object):

	# ("Motor Cogwheel Diameter" / "Rear Wheel Diameter") *
	#   "Rear Wheel Circumfence" *
	#   ("Minutes in an hour" / "Meters in a kilometer")
	GEARBOX_AND_WHEEL_RATIO = (32.0 / 144.0) * 2.038 * (60.0 / 1000.0)

	def __init__(self):
		self.motor_rms_current = 0
		self.actual_speed = 0
		self.battery_current = 0
		self.dc_capacitor_voltage = 0

	def parse(self, data):
		self.motor_rms_current = int(parse_unsigned_int(data, 0, 16) / 10.0)
		self.actual_speed = parse_signed_int(data, 16, 16)
		self.battery_current = int(parse_signed_int(data, 32, 16) / 10.0)
		self.dc_capacitor_voltage = (parse_unsigned_int(data, 48, 16) / 64.0)

	def __str__(self):
		s1 = "%25s: % .01f" % ("RMS Current", self.motor_rms_current)
		s2 = "%25s: % 3d" % ("Actual Speed", self.actual_speed)
		s3 = "%25s: % .01f" % ("Battery Current", self.battery_current)
		s4 = "%25s: % .01f" % ("DC Capacitor Voltage", self.dc_capacitor_voltage)

		return "\n".join([s1, s2, s3, s4])

	def get_speed(self):
		rpm = self.actual_speed

		if rpm > 1.0:
			speed = self.GEARBOX_AND_WHEEL_RATIO * rpm
		else:
			speed = 0.0

		return speed

class Msg_2a6(object):
	STATES = ["Open", "Precharge", "Weld Check", "Closing Delay", "Missing Check",
	"Closed (When Main Enable = On)", "Delay", "Arc Check", "Open Delay", "Fault",
	"Closed (When Main Enable = Off)"]

	def __init__(self):

		self.motor_temp = 0
		self.controller_temp = 0
		self.sstate = "N/A"
		self.status = 0
		self.motor_power = 0

	def parse(self, data):

		self.motor_temp = parse_signed_int(data, 0, 16) / 10.0
		self.controller_temp = parse_signed_int(data, 16, 16) / 10.0

		state = parse_unsigned_int(data, 32, 8)
		if state >= len(self.STATES):
			self.sstate = "Unknown State! " + str(state)
		else:
			self.sstate = self.STATES[state]

		self.status = parse_unsigned_int(data, 40, 8)
		self.motor_power = parse_signed_int(data, 48, 16) / 10.0

	def __str__(self):
		s1 = "%25s: % .01f" % ("Motor Temperature", self.motor_temp)
		s2 = "%25s: % .01f" % ("Controller Temperature", self.controller_temp)
		s3 = "%25s:  %s" % ("State", self.sstate)
		s4 = "%25s: % d" % ("Status", self.status)
		s5 = "%25s: % d" % ("Motor Power", self.motor_power)

		return "\n".join([s1, s2, s3, s4, s5])


class Msg_3a6(object):

	def __init__(self):
		self.error_code = 0
		self.vehicle_acc = 0
		self.odometer = 0

	def parse(self, data):
		self.error_code = parse_unsigned_int(data, 0, 8)
		self.vehicle_acc = parse_signed_int(data, 16, 16) / 1000.0
		self.odometer = parse_unsigned_int(data, 32, 32) / 10.0

	def __str__(self):
		s1 = "%25s: % d" % ("Error Code", self.error_code)
		s2 = "%25s: % .03f" % ("Vehicle Acceleration", self.vehicle_acc)
		s3 = "%25s: % .01f" % ("Odometer", self.odometer)

		return "\n".join([s1, s2, s3])


class Msg_4a6(object):

	def __init__(self):
		self.tts_1 = 0
		self.tts_2 = 0
		self.dcdc = 0

	def parse(self, data):
		self.tts_1 = parse_unsigned_int(data, 0, 16)
		self.tts_2 = parse_signed_int(data, 16, 16)
		self.dcdc = parse_unsigned_int(data, 48, 16)/100.0

	def __str__(self):
		s1 = "%25s: % d" % ("Time to Speed 1", self.tts_1)
		s2 = "%25s: % d" % ("Time to Speed 2", self.tts_2)
		s3 = "%25s: % .01f" % ("DC-DC", self.dcdc)

		return "\n".join([s1, s2, s3])

