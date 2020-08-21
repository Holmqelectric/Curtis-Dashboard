#!/usr/bin/python -B
# -*- coding: utf-8 -*-

class DashboardSettings(object):

	DEBUG = False

	SOFT_TURN_SIGNAL_MAX = 4
	HARD_TURN_SIGNAL_LIMIT = 3

	BATTERY_TOTAL_ENERGY = 8800*60*60 # W seconds
	STORE_STATE_INTERVAL = 600 # Nr. seconds * 10
	DEFAULT_ENERGY_CONSUMPTION = 300.0

	#
	# PiCAN reserved pins
	#
	# GPIO 05	29 (CHECK)
	# GPIO 17	11
	# GPIO 19	35
	# GPIO 22	15 (CONFIRMED)
	# GPIO 25	22 (CONFIRMED)
	# GPIO 26	37 (CHECK)
	# GPIO 27	13
	#
	#
	# (ALL SPI CONFIRMED)
	# SPI0_MOSI	19
	# SPI0_MISO	21
	# SPI0_SCLK	23
	# SPI0_CE0	24
	#
	# UART0_RX	10
	# UART0_TX	8

	# ---------------------

	# taken pins [8, 10, 11, 13, 15, 19, 21, 22, 23, 24, 29, 35, 37]

	#
	#
	#	GPIO Pin settings
	#
	#

	# relay_pins = [31, 33, 32, 36, 38]
	# input pins = [18, 16, 12, 7, 40]

	TURN_LEFT_OUT_PCB_PIN = 31
	TURN_RIGHT_OUT_PCB_PIN = 33
	HIGHBEAM_OUT_PCB_PIN = 32
	BRAKE_LIGHT_OUT_PCB_PIN = 36
	HORN_OUT_PCB_PIN = 38
	#RUN_OUT_PCB_PIN = 40

	TURN_LEFT_IN_PCB_PIN = 40
	TURN_RIGHT_IN_PCB_PIN = 18
	HIGHBEAM_IN_PCB_PIN = 16
	BRAKE_LIGHT_IN_PCB_PIN = 12
	HORN_IN_PCB_PIN = 7

	IN_PINS = [
		TURN_LEFT_IN_PCB_PIN,
		TURN_RIGHT_IN_PCB_PIN,
		HIGHBEAM_IN_PCB_PIN,
		#RUNNING_LIGHT_IN_PCB_PIN,
		BRAKE_LIGHT_IN_PCB_PIN,
		HORN_IN_PCB_PIN
	]

	OUT_PINS = [
		TURN_LEFT_OUT_PCB_PIN,
		TURN_RIGHT_OUT_PCB_PIN,
		HIGHBEAM_OUT_PCB_PIN,
		#RUNNING_LIGHT_OUT_PCB_PIN,
		BRAKE_LIGHT_OUT_PCB_PIN,
		HORN_OUT_PCB_PIN
	]


	#
	#
	#	GUI settings
	#
	#
	LEFT_TURN_BBOX = [(15,0), (15,90), (100, 90), (100, 0)]
	RIGHT_TURN_BBOX = [(695, 0), (695, 90), (800, 90), (800, 0)]
	WARN_LIGHT_BBOX = [(145, 0), (145, 90), (240, 90), (240, 0)]
	HIGHBEAM_BBOX = [(545, 0), (545, 90), (670, 90), (670, 0)]
	RANGE_BBOX = [(600, 135), (600, 185), (660, 185), (660, 135)]
