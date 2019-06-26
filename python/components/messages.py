#!/usr/bin/python -B
# -*- coding: utf-8 -*-
import struct
import time
import threading
import pickle
import os

from components.settings import DashboardSettings as DS

path = os.path.dirname(os.path.realpath(__file__))

STATE_PICKLE_PATH = "%s/../../state.pickle" % (path)

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

#
# Class for disk storage
#
class DumpStates(object):
	def __init__(self):
		self.energy_state = 0.0
		self.consumption = ConsumptionData()

	def put_states(self, o):
		o.energy_state = self.energy_state
		o.consumption = self.consumption

	def get_states(self, o):
		self.energy_state = o.energy_state
		self.consumption = o.consumption

#
# Simple fixed size rotating list
#
class RotatingList(object):

	def __init__(self, size):
		self.index = 0
		self.data = [(DS.DEFAULT_ENERGY_CONSUMPTION*1000.0, 1000.0)]*size

	def append(self, value):
		self.data[self.index] = value
		self.index += 1
		if self.index >= len(self.data):
			self.index = 0

	def get_latest(self):
		index = self.index - 1
		if index < 0:
			index = len(self.data) - 1

		return self.data[index]

class ConsumptionData(object):
	def __init__(self):
		#
		# Three layers of data storage.
		# - High frequency
		# - Seconds
		# - Minutes
		#
		self.hfdata = []
		self.hfreset = None
		self.sdata = []
		self.mdata = RotatingList(10)

		# Simple calculation caching
		self.added = True
		self.calculated = 0.0

	def append(self, energy_rate, speed, dt):

		#
		# Add all data to the High Frequency list if speed is big enough
		#
		if speed < 1.0:
			return

		self.hfdata.append((energy_rate, speed * dt))

		t = time.time()

		# If this is the first element, then only set timestamp
		if self.hfreset is None:
			self.hfreset = t
			return

		#
		# Calculate average of HF-list each second and put in second list
		#
		if (self.hfreset + 1.0) < t and len(self.hfdata) > 0:
			# Sum column wise
			te, td = map(sum, zip(*self.hfdata))

			# Add data and clear previous
			self.sdata.append((te, td))
			self.hfdata = []
			self.hfreset = t

		#
		# When we have a full minute, copy over average to minute list
		# Minute list contains a fixed set of minutes.
		#
		if len(self.sdata) > 60:

			te, td = map(sum, zip(*self.sdata))

			self.mdata.append((te, td))
			self.added = True
			self.sdata = []

			# DEBUG
			ss = ", ".join([ "%.0f:%.0f" % (e,d) for e,d in self.mdata.data])
			cons = self.get_avg_consumption()

			print("Consuption list:", ss)
			print("Avg consumption:", "%.01f" % cons)


	def get_avg_consumption(self):

		if not self.added:
			return self.calculated

		self.added = False

		# Sum tuples, column by column
		te, td = map(sum, zip(*self.mdata.data))

		self.calculated = te/td

		return self.calculated

	def get_latest_consumption(self):
		e, d = self.mdata.get_latest()

		return e/d

class StateData(object):
	# ("Motor Cogwheel Diameter" / "Rear Cogwheel Diameter") *
	#   "Rear Wheel Circumfence"
	GEARBOX_AND_WHEEL_RATIO = (24.0 / 144.0) * 2.040

	STATES = ["Open", "Precharge", "Weld Check", "Closing Delay", "Missing Check",
	"Closed (When Main Enable = On)", "Delay", "Arc Check", "Open Delay", "Fault",
	"Closed (When Main Enable = Off)"]

	def __init__(self):
		#
		# CAN data variables
		#
		self.motor_rms_current = 0
		self.actual_speed = 0
		self.battery_current = 0
		self.dc_capacitor_voltage = 0.0

		self.motor_temp = 0
		self.controller_temp = 0
		self.sstate = "N/A"
		self.status = 0
		self.motor_power = 0.0

		self.error_code = 0
		self.vehicle_acc = 0
		self.odometer = 0

		self.tts_1 = 0
		self.tts_2 = 0
		self.dcdc = 0

		#
		# Update timestamps
		#
		self.mp_update_time = None
		self.as_update_time = None

		#
		# Current enery and consumption data
		#
		self.energy_state = DS.BATTERY_TOTAL_ENERGY
		self.energy_rate = 0.0
		self.consumption = ConsumptionData()

		self.write_lock = threading.Lock()

		# Load data stored on disk
		self.load_states()

	def parse_m1(self, data):

		self.write_lock.acquire()

		self.motor_rms_current = int(parse_unsigned_int(data, 0, 16) / 10.0)
		self.battery_current = int(parse_signed_int(data, 32, 16) / 10.0)
		self.dc_capacitor_voltage = (parse_unsigned_int(data, 48, 16) / 64.0)

		# Reset available energy in battery if voltage is high
		if self.dc_capacitor_voltage >= 168.0:
			self.energy_state = DS.BATTERY_TOTAL_ENERGY

		actual_speed = parse_signed_int(data, 16, 16)

		# Store consumption data
		t = time.time()
		if self.as_update_time is not None:
			dt = t - self.as_update_time
			speed = (self.get_speed_ms(actual_speed) + self.get_speed_ms())/2.0
			self.consumption.append(self.energy_rate, speed, dt)

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

		motor_power = parse_signed_int(data, 48, 16) * 10.0

		# Subtract used energy
		t = time.time()
		if self.mp_update_time is not None:
			dt = t - self.mp_update_time
			power = (motor_power + self.motor_power)/2.0
			energy_rate = power*dt
			self.energy_state -= energy_rate
			self.energy_rate = energy_rate

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

	def get_speed_ms(self, rpm=None):
		if rpm is None:
			rpm = self.actual_speed

		if rpm > 1.0:
			speed = (self.GEARBOX_AND_WHEEL_RATIO * rpm * 1.01) / 60.0
		else:
			speed = 0.0

		return speed

	def get_speed_kmh(self):
		return self.get_speed_ms(self.actual_speed) * (3600.0 / 1000.0)

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

	def get_consumption_kwh(self):
		return self.consumption.get_latest_consumption()/360.0

	def get_range(self):

		cc = self.consumption.get_avg_consumption()
		range = self.energy_state/cc

		return range

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

