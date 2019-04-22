#!/usr/bin/python -B
# -*- coding: utf-8 -*-
import threading
import time

from components.settings import DashboardSettings as DS


if DS.DEBUG:
	from .dummy_pi import GPIO as GPIO
else:
	import RPi.GPIO as GPIO

RELAY_OFF = GPIO.HIGH
RELAY_ON = GPIO.LOW

# Separate thread to handle the timed blinking of turn signal
class TurnHandler(threading.Thread):
	def __init__(self, shutdown, interval=0.5):
		super().__init__()
		self.shutdown = shutdown

		# Blink interval
		self.interval = interval

		# Active means that we are blinking ...
		self.left_active = False
		self.right_active = False
		# ... state means if the light is on or off
		self.left_state = False
		self.right_state = False

		# If set then we blink forever
		self.hard_turn_signal = False

		self.cycle_count = 0

		GPIO.output(DS.TURN_LEFT_OUT_PCB_PIN, RELAY_OFF)
		GPIO.output(DS.TURN_RIGHT_OUT_PCB_PIN, RELAY_OFF)

	def activate_left(self):
		self.left_active = True
		# Start off with false because it is swapped directly in the run loop
		self.left_state = False
		self.cycle_count = 0

	def activate_right(self):
		self.right_active = True
		self.right_state = False
		self.cycle_count = 0

	def deactivate_left(self):
		self.left_active = False
		self.left_state = False
		#self.hard_turn_signal = False

	def deactivate_right(self):
		self.right_active = False
		self.right_state = False
		#self.hard_turn_signal = False

	def run(self):
		do_once = False
		while not self.shutdown.is_set():

			while (self.left_active or self.right_active) and not self.shutdown.is_set():
				do_once = True
				if self.left_active:
					self.left_state = not self.left_state
					gpiostate = RELAY_ON if self.left_state else RELAY_OFF
					GPIO.output(DS.TURN_LEFT_OUT_PCB_PIN, gpiostate)

				if self.right_active:
					self.right_state = not self.right_state
					gpiostate = RELAY_ON if self.right_state else RELAY_OFF
					GPIO.output(DS.TURN_RIGHT_OUT_PCB_PIN, gpiostate)

				# Auto shut off if we reach soft limit
				if self.hard_turn_signal is False:
					if self.cycle_count > DS.SOFT_TURN_SIGNAL_MAX:
						self.deactivate_right()
						self.deactivate_left()
						break

				self.cycle_count += 1
				time.sleep(self.interval)

			if do_once:
				# Make sure to finally turn lights off
				do_once = False
				GPIO.output(DS.TURN_LEFT_OUT_PCB_PIN, RELAY_OFF)
				GPIO.output(DS.TURN_RIGHT_OUT_PCB_PIN, RELAY_OFF)

			# Note the indent
			time.sleep(0.1)



class EventHandler(threading.Thread):

	def __init__(self, objects, shutdown, replay_mode=True):
		super().__init__()
		self.objects = objects
		self.shutdown = shutdown
		GPIO.setmode(GPIO.BOARD)

		for pin in DS.IN_PINS:
			GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

		for pin in DS.OUT_PINS:
			GPIO.setup(pin, GPIO.OUT)

		self.turn_signal = TurnHandler(shutdown)
		self.turn_signal.start()

		self.warning_active = False
		self.highbeam_active = False

	def toggle_right_turn(self):
		if not self.warning_active:
			self.turn_signal.deactivate_left()
			if self.turn_signal.right_active:
				self.turn_signal.deactivate_right()
			else:
				self.turn_signal.activate_right()

	def toggle_left_turn(self):
		if not self.warning_active:
			self.turn_signal.deactivate_right()
			if self.turn_signal.left_active:
				self.turn_signal.deactivate_left()
			else:
				self.turn_signal.activate_left()

	def set_turn_duration(self, is_long):
		self.turn_signal.hard_turn_signal = is_long

	def toggle_warning(self):
		if not self.warning_active:
			self.warning_active = True
			self.turn_signal.hard_turn_signal = True
			self.turn_signal.activate_left()
			self.turn_signal.activate_right()
		else:
			self.warning_active = False
			self.turn_signal.deactivate_left()
			self.turn_signal.deactivate_right()

	def toggle_highbeam(self):
		self.highbeam_active = not self.highbeam_active
		gpiostate = RELAY_ON if self.highbeam_active else RELAY_OFF
		GPIO.output(DS.HIGHBEAM_OUT_PCB_PIN, gpiostate)

	def set_highbeam(self, state):
		self.highbeam_active = state
		gpiostate = RELAY_ON if self.highbeam_active else RELAY_OFF
		GPIO.output(DS.HIGHBEAM_OUT_PCB_PIN, gpiostate)

	def set_brake(self, state):
		gpiostate = RELAY_ON if state else RELAY_OFF
		GPIO.output(DS.BRAKE_LIGHT_OUT_PCB_PIN, gpiostate)

	def set_horn(self, state):
		gpiostate = RELAY_ON if state else RELAY_OFF
		GPIO.output(DS.HORN_OUT_PCB_PIN, gpiostate)

	def wait_for_release(self, pin_number):
		wait_count = 0
		while GPIO.input(pin_number) == GPIO.HIGH and not self.shutdown.is_set():
			wait_count += 1
			time.sleep(0.1)
		return wait_count

	def run(self):

		while not self.shutdown.is_set():

			pinstate = GPIO.input(DS.BRAKE_LIGHT_IN_PCB_PIN)
			if pinstate == GPIO.HIGH:
				self.set_brake(True)
			else:
				self.set_brake(False)

			pinstate = GPIO.input(DS.HIGHBEAM_IN_PCB_PIN)
			if pinstate == GPIO.HIGH:
				self.set_highbeam(True)
			else:
				self.set_highbeam(False)

			pinstate = GPIO.input(DS.HORN_IN_PCB_PIN)
			if pinstate == GPIO.HIGH:
				self.set_horn(True)
			else:
				self.set_horn(False)


			pinstate = GPIO.input(DS.TURN_LEFT_IN_PCB_PIN)
			if pinstate == GPIO.HIGH:
				self.toggle_left_turn()

				# Wait until the button is released
				wait_count = self.wait_for_release(DS.TURN_LEFT_IN_PCB_PIN)

				# If we hold it long enough we should blink until button pushed next time
				self.set_turn_duration(wait_count > DS.HARD_TURN_SIGNAL_LIMIT)

			pinstate = GPIO.input(DS.TURN_RIGHT_IN_PCB_PIN)
			if pinstate == GPIO.HIGH:
				self.toggle_right_turn()

				# Wait until the button is released
				wait_count = self.wait_for_release(DS.TURN_RIGHT_IN_PCB_PIN)

				# If we hold it long enough we should blink until button pushed next time
				self.set_turn_duration(wait_count > DS.HARD_TURN_SIGNAL_LIMIT)

			time.sleep(0.1)

		time.sleep(1.0)
		GPIO.cleanup()
