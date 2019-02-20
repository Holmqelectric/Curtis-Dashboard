#!/usr/bin/python -B
# -*- coding: utf-8 -*-

class DashboardSettings(object):

	DEBUG = False

	SOFT_TURN_SIGNAL_MAX = 4
	HARD_TURN_SIGNAL_LIMIT = 3


	#
	#
	#	GPIO Pin settings
	#
	#

	# relay_pins = [31, 33, 35, 37, 32, 36, 38, 40]
	# input pins = [29, 22, 18, 16, 15, 13, 11, 12]

	TURN_LEFT_OUT_PCB_PIN = 37
	TURN_RIGHT_OUT_PCB_PIN = 16
	HIGHBEAM_OUT_PCB_PIN = 35
	RUNNING_LIGHT_OUT_PCB_PIN = 40
	BRAKE_LIGHT_OUT_PCB_PIN = 32
	HORN_OUT_PCB_PIN = 36

	TURN_LEFT_IN_PCB_PIN = 38
	TURN_RIGHT_IN_PCB_PIN = 18
	HIGHBEAM_IN_PCB_PIN = 18
	RUNNING_LIGHT_IN_PCB_PIN = 16
	BRAKE_LIGHT_IN_PCB_PIN = 15
	HORN_IN_PCB_PIN = 13

	IN_PINS = [
		TURN_LEFT_IN_PCB_PIN,
		TURN_RIGHT_IN_PCB_PIN,
		#HIGHBEAM_IN_PCB_PIN,
		#RUNNING_LIGHT_IN_PCB_PIN,
		#BRAKE_LIGHT_IN_PCB_PIN,
		#HORN_IN_PCB_PIN
	]

	OUT_PINS = [
		TURN_LEFT_OUT_PCB_PIN,
		TURN_RIGHT_OUT_PCB_PIN,
		#HIGHBEAM_OUT_PCB_PIN,
		#RUNNING_LIGHT_OUT_PCB_PIN,
		#BRAKE_LIGHT_OUT_PCB_PIN,
		#HORN_OUT_PCB_PIN
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
