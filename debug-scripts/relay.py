#!/usr/bin/python -B
# -*- coding: utf-8 -*-

import sys
import os
import signal
import argparse
import time

from threading import Event

import RPi.GPIO as GPIO

shutdown = Event()

# Pin Definitons:
#relay_pins = [31, 33, 35, 37, 32, 36, 38, 40]
relay_pins = [40]

def setup_pins():

	# Board numbering
	GPIO.setmode(GPIO.BOARD)

	for pin in relay_pins:
		GPIO.setup(pin, GPIO.OUT)
		GPIO.output(pin, GPIO.HIGH)

def run(infile):
	global shutdown

	setup_pins()

	relay_up = True
	while not shutdown.is_set():
		time.sleep(0.5)
		for pin in relay_pins:
			if relay_up:
				GPIO.output(pin, GPIO.LOW)
			else:
				GPIO.output(pin, GPIO.HIGH)

		relay_up = not relay_up

	GPIO.cleanup()  # cleanup all GPIO

def exit_handler(sig, frame):
	global shutdown
	print("Caught Ctrl-C, will exit")
	shutdown.set()
	sys.exit(1)


if __name__ == "__main__":
	signal.signal(signal.SIGINT, exit_handler)

	parser = argparse.ArgumentParser(description='Process CAN data')

	args = parser.parse_args()

	# make stdin a non-blocking file
	#fd = sys.stdin.fileno()
	#fl = fcntl.fcntl(fd, fcntl.F_GETFL)
	#fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

	run(sys.stdin)

