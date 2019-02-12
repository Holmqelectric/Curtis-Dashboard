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

	def __init__(self):
		self.motor_rms_current = 0
		self.actual_speed = 0
		self.battery_current = 0
		self.dc_capacitor_voltage = 0

	def parse(self, data):
		self.motor_rms_current = parse_unsigned_int(data, 0, 16) / 10.0
		self.actual_speed = parse_signed_int(data, 16, 16)
		self.battery_current = parse_signed_int(data, 32, 16) / 10.0
		self.dc_capacitor_voltage = (parse_unsigned_int(data, 48, 16) / 64.0)

	def __str__(self):
		s1 = "           RMS Current: % .01f" % (self.motor_rms_current)
		s2 = "          Actual Speed: % 3d" % (self.actual_speed)
		s3 = "       Battery Current: % .01f" % (self.battery_current)
		s4 = "  DC Capacitor Voltage: % .01f" % (self.dc_capacitor_voltage)

		return "\n".join([s1, s2, s3, s4])

	def get_speed(self):
		rpm = self.actual_speed

		if rpm > 1.0:
			speed = (32.0 / 144.0) * rpm * 2.038 * (60.0 / 1000.0)
		else:
			speed = 0.0

		return speed

class Msg_2a6(object):

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
		if state == 0:
			self.sstate = "Open"
		elif state == 1:
			self.sstate = "Precharge"
		elif state == 2:
			self.sstate = "Weld Check"
		elif state == 3:
			self.sstate = "Closing Delay"
		elif state == 4:
			self.sstate = "Missing Check"
		elif state == 5:
			self.sstate = "Closed (When Main Enable = On)"
		elif state == 6:
			self.sstate = "Delay"
		elif state == 7:
			self.sstate = "Arc Check"
		elif state == 8:
			self.sstate = "Open Delay"
		elif state == 9:
			self.sstate = "Fault"
		elif state == 10:
			self.sstate = "Closed (When Main Enable = Off)"
		else:
			self.sstate = "Unknown State! " + str(state)

		self.status = parse_unsigned_int(data, 40, 8)
		self.motor_power = parse_signed_int(data, 48, 16)

	def __str__(self):
		s1 = "     Motor Temperature: % .01f" % (self.motor_temp)
		s2 = "Controller Temperature: % .01f" % (self.controller_temp)
		s3 = "                 State:  %s" % (self.sstate)
		s4 = "                Status: % d" % (self.status)
		s5 = "           Motor Power: % d" % (self.motor_power)

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
		s1 = "            Error Code: % d" % (self.error_code)
		s2 = "  Vehicle Acceleration: % .03f" % (self.vehicle_acc)
		s3 = "              Odometer: % .01f" % (self.odometer)

		return "\n".join([s1, s2, s3])


class Msg_4a6(object):

	def __init__(self):
		self.tts_1 = 0
		self.tts_2 = 0

	def parse(self, data):
		self.tts_1 = parse_unsigned_int(data, 0, 16)
		self.tts_2 = parse_signed_int(data, 16, 16)

	def __str__(self):
		s1 = "       Time to Speed 1: % d" % (self.tts_1)
		s2 = "       Time to Speed 2: % d" % (self.tts_2)

		return "\n".join([s1, s2])

