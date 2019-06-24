#!/usr/bin/python -B
# -*- coding: utf-8 -*-
import struct
import time
import threading
import pickle
import os

from components.settings import DashboardSettings as DS

STATE_PICKLE_PATH = "/tmp/state.pickle"

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

class DumpStates(object):
	def __init__(self):
		self.energy_state = 0.0
		self.distance_state = 0.0
		self.old_energy_state = 0.0
		self.old_distance_state = 0.0

	def put_states(self, o):
		o.energy_state = self.energy_state
		o.old_energy_state = self.old_energy_state
		o.distance_state = self.distance_state
		o.old_distance_state = self.old_distance_state

	def get_states(self, o):
		self.energy_state = o.energy_state
		self.old_energy_state = o.old_energy_state
		self.distance_state = o.distance_state
		self.old_distance_state = o.old_distance_state


class StateData(object):
	# ("Motor Cogwheel Diameter" / "Rear Cogwheel Diameter") *
	#   "Rear Wheel Circumfence" *
	#   ("Minutes in an hour" / "Meters in a kilometer")
	GEARBOX_AND_WHEEL_RATIO = (24.0 / 144.0) * 2.040

	STATES = ["Open", "Precharge", "Weld Check", "Closing Delay", "Missing Check",
	"Closed (When Main Enable = On)", "Delay", "Arc Check", "Open Delay", "Fault",
	"Closed (When Main Enable = Off)"]

	def __init__(self):
		self.motor_rms_current = 0
		self.actual_speed = 0
		self.battery_current = 0
		self.dc_capacitor_voltage = 0

		self.motor_temp = 0
		self.controller_temp = 0
		self.sstate = "N/A"
		self.status = 0
		self.motor_power = 0

		self.error_code = 0
		self.vehicle_acc = 0
		self.odometer = 0

		self.tts_1 = 0
		self.tts_2 = 0
		self.dcdc = 0

		self.mp_update_time = None
		self.as_update_time = None

		self.energy_state = DS.BATTERY_TOTAL_ENERGY
		self.distance_state = 0.0

		self.old_energy_state = DS.BATTERY_TOTAL_ENERGY
		self.old_distance_state = 0.0

		self.range = 110000.0

		self.write_lock = threading.Lock()

		self.load_states()

	def parse_m1(self, data):

		self.write_lock.acquire()
		self.motor_rms_current = int(parse_unsigned_int(data, 0, 16) / 10.0)
		self.battery_current = int(parse_signed_int(data, 32, 16) / 10.0)
		self.dc_capacitor_voltage = (parse_unsigned_int(data, 48, 16) / 64.0)

		if self.dc_capacitor_voltage >= 168.0:
			self.energy_state = DS.BATTERY_TOTAL_ENERGY
			self.distance_state = 0.0

		actual_speed = parse_signed_int(data, 16, 16)

		t = time.time()
		if self.as_update_time is not None:
			dt = t - self.as_update_time
			speed = (self.__get_speed(actual_speed) + self.__get_speed(self.actual_speed))/2.0
			self.distance_state += speed*dt

		self.as_update_time = t
		self.actual_speed = actual_speed

		self.write_lock.release()

	def parse_m2(self, data):

		self.write_lock.acquire()
		self.motor_temp = parse_signed_int(data, 0, 16) / 10.0
		self.controller_temp = parse_signed_int(data, 16, 16) / 10.0

		state = parse_unsigned_int(data, 32, 8)
		if state >= len(self.STATES):
			self.sstate = "Unknown State! " + str(state)
		else:
			self.sstate = self.STATES[state]

		self.status = parse_unsigned_int(data, 40, 8)

		motor_power = parse_signed_int(data, 48, 16) * 100.0

		t = time.time()
		if self.mp_update_time is not None:
			dt = t - self.mp_update_time
			power = (motor_power + self.motor_power)/2.0
			self.energy_state -= power*dt

		self.mp_update_time = t
		self.motor_power = motor_power
		self.write_lock.release()

	def parse_m3(self, data):
		self.write_lock.acquire()
		self.error_code = parse_unsigned_int(data, 0, 8)
		self.vehicle_acc = parse_signed_int(data, 16, 16) / 1000.0
		self.odometer = parse_unsigned_int(data, 32, 32) / 10.0
		self.write_lock.release()

	def parse_m4(self, data):
		self.write_lock.acquire()
		self.tts_1 = parse_unsigned_int(data, 0, 16)
		self.tts_2 = parse_signed_int(data, 16, 16)
		self.dcdc = parse_unsigned_int(data, 48, 16)/100.0
		self.write_lock.release()

	def dump_states(self):
		self.write_lock.acquire()
		f = open(STATE_PICKLE_PATH, 'wb')
		o = DumpStates()
		o.get_states(self)

		pickle.dump(o, f, pickle.HIGHEST_PROTOCOL)

		f.flush()
		f.close()
		self.write_lock.release()

	def load_states(self):
		if os.path.isfile(STATE_PICKLE_PATH):
			f = open(STATE_PICKLE_PATH, 'rb')
			o = pickle.load(f)
			o.put_states(self)
			f.close()


	# Returns speed in 'meters per second'
	def __get_speed(self, rpm):
		if rpm > 1.0:
			speed = (self.GEARBOX_AND_WHEEL_RATIO * rpm * 1.01) / 60.0
		else:
			speed = 0.0

		return speed

	def get_speed_kmh(self):
		return self.__get_speed(self.actual_speed) * (3600.0 / 1000.0)

	def get_speed_ms(self):
		return self.__get_speed(self.actual_speed)

	def get_dc_capacitor_voltage(self):
		return self.dc_capacitor_voltage

	def get_motor_power(self):
		return max(self.motor_power, 0.0)/1000.0

	def get_actual_speed(self):
		return max(self.actual_speed, 0)

	def get_motor_rms_current(self):
		return int(max(self.motor_rms_current, 0))

	def get_odometer(self):
		return max(self.odometer, 0)

	def get_controller_temp(self):
		return max(self.controller_temp, 0)

	def get_motor_temp(self):
		return max(self.motor_temp, 0)

	def get_dcdc(self):
		return max(self.dcdc, 0)

	def get_soc_percent(self):
		return self.energy_state/DS.BATTERY_TOTAL_ENERGY

	def get_range(self):

		dE = self.old_energy_state - self.energy_state
		dS = self.distance_state - self.old_distance_state

		if dS < 10.0 or dE < 10.0:
			return 110000.0

		x = (self.energy_state/dE)*dS
		self.range = (10*self.range + x)/11.0

		return self.range

	def __str__(self):

		ret = []
		ret.append(self.__str_m1__())
		ret.append(self.__str_m2__())
		ret.append(self.__str_m3__())
		ret.append(self.__str_m4__())
		return "\n".join(ret)

	def __str_m1__(self):
		s1 = "%25s: % .01f" % ("RMS Current", self.motor_rms_current)
		s2 = "%25s: % 3d" % ("Actual Speed", self.actual_speed)
		s3 = "%25s: % .01f" % ("Battery Current", self.battery_current)
		s4 = "%25s: % .01f" % ("DC Capacitor Voltage", self.dc_capacitor_voltage)

		return "\n".join([s1, s2, s3, s4])

	def __str_m2__(self):
		s1 = "%25s: % .01f" % ("Motor Temperature", self.motor_temp)
		s2 = "%25s: % .01f" % ("Controller Temperature", self.controller_temp)
		s3 = "%25s:  %s" % ("State", self.sstate)
		s4 = "%25s: % d" % ("Status", self.status)
		s5 = "%25s: % d" % ("Motor Power", self.motor_power)

		return "\n".join([s1, s2, s3, s4, s5])

	def __str_m3__(self):
		s1 = "%25s: % d" % ("Error Code", self.error_code)
		s2 = "%25s: % .03f" % ("Vehicle Acceleration", self.vehicle_acc)
		s3 = "%25s: % .01f" % ("Odometer", self.odometer)

		return "\n".join([s1, s2, s3])

	def __str_m4__(self):
		s1 = "%25s: % d" % ("Time to Speed 1", self.tts_1)
		s2 = "%25s: % d" % ("Time to Speed 2", self.tts_2)
		s3 = "%25s: % .01f" % ("DC-DC", self.dcdc)

		return "\n".join([s1, s2, s3])

