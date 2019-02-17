#!/usr/bin/python -B
# -*- coding: utf-8 -*-
import threading
import time

from components.settings import DashboardSettings as DS

debug = False

if debug:
	from .dummy_pi import GPIO as GPIO
else:
	import RPi.GPIO as GPIO


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

	def activate_left(self):
		self.left_active = True
		# Start off with false because it is swapped directly in the run loop
		self.left_state = False

	def activate_right(self):
		self.right_active = True
		self.right_state = False

	def deactivate_left(self):
		self.left_active = False
		self.left_state = False

	def deactivate_right(self):
		self.right_active = False
		self.right_state = False

	def run(self):
		do_once = False
		while not self.shutdown.is_set():

			while (self.left_active or self.right_active) and not self.shutdown.is_set():
				do_once = True
				if self.left_active:
					self.left_state = not self.left_state
					gpiostate = GPIO.HIGH if self.left_state else GPIO.LOW
					GPIO.output(DS.TURN_LEFT_OUT_PCB_PIN, gpiostate)

				if self.right_active:
					self.right_state = not self.right_state
					gpiostate = GPIO.HIGH if self.right_state else GPIO.LOW
					GPIO.output(DS.TURN_RIGHT_OUT_PCB_PIN, gpiostate)


				time.sleep(self.interval)

			if do_once:
				# Make sure to finally turn lights off
				do_once = False
				GPIO.output(DS.TURN_LEFT_OUT_PCB_PIN, GPIO.LOW)
				GPIO.output(DS.TURN_RIGHT_OUT_PCB_PIN, GPIO.LOW)

			# Note the indent
			time.sleep(0.1)



class EventHandler(threading.Thread):

	def __init__(self, objects, shutdown, replay_mode=True):
		super().__init__()
		self.objects = objects
		self.shutdown = shutdown
		GPIO.setmode(GPIO.BOARD)

		for pin in DS.IN_PINS:
			GPIO.setup(pin, GPIO.IN)

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

	def toggle_warning(self):
		if not self.warning_active:
			self.warning_active = True
			self.turn_signal.activate_left()
			self.turn_signal.activate_right()
		else:
			self.warning_active = False
			self.turn_signal.deactivate_left()
			self.turn_signal.deactivate_right()

	def toggle_highbeam(self):
		self.highbeam_active = not self.highbeam_active
		gpiostate = GPIO.HIGH if self.highbeam_active else GPIO.LOW
		GPIO.output(DS.HIGHBEAM_OUT_PCB_PIN, gpiostate)

	def run(self):

		prev_time = -1
		while not self.shutdown.is_set():

			time.sleep(0.1)
