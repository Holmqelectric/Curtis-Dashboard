#!/usr/bin/python -B
# -*- coding: utf-8 -*-

import fcntl
import sys
import os
import signal
import argparse
import time

from threading import Event

from components.settings import DashboardSettings as DS
from components.messages import *


# Global semaphore that makes all threads quit
shutdown = Event()


def run(infile, replay_mode, fullscreen):

	global shutdown

	objects = [Msg_1a6(), Msg_2a6(), Msg_3a6(), Msg_4a6()]

	c = CanReader(objects, infile, shutdown, replay_mode)
	c.start()

	evh = EventHandler(objects, shutdown)
	evh.start()

	gui = FlukeGUI(objects, evh, shutdown, fullscreen)
	gui.start()

	# Let the main sleep until everyone has acknowledged the shutdown
	while not shutdown.is_set():
		time.sleep(0.1)

	c.join()
	evh.join()
	gui.join()


def run_profile(infile, replay_mode, fullscreen):
	import cProfile
	pr = cProfile.Profile()
	pr.enable()
	run(sys.stdin, args.run_replay, args.use_fullscreen)
	pr.disable()
	pr.print_stats(sort="calls")



def exit_handler(sig, frame):
	global shutdown
	print("Caught Ctrl-C, will exit")
	shutdown.set()


if __name__ == "__main__":
	signal.signal(signal.SIGINT, exit_handler)

	parser = argparse.ArgumentParser(description='Process CAN data')
	parser.add_argument('-r', '--replay', dest='run_replay', action='store_true',
						help='Run in replay mode, default false')
	parser.add_argument('-f', '--fullscreen', dest='use_fullscreen', action='store_true',
						help='Run in fullscreen mode, default false')
	parser.add_argument('-d', dest='debug', action='store_true',
						help='Start in debug mode')

	args = parser.parse_args()

	if args.debug:
		DS.DEBUG = True

	# Late import to acknowledge the debug flag
	from components.canreader import CanReader
	from components.eventhandler import EventHandler
	from components.flukegui import FlukeGUI

	# make stdin a non-blocking file
	fd = sys.stdin.fileno()
	fl = fcntl.fcntl(fd, fcntl.F_GETFL)
	fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

	run(sys.stdin, args.run_replay, args.use_fullscreen)
	#run_profile(sys.stdin, args.run_replay, args.use_fullscreen, args.use_mega)

