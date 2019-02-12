#!/usr/bin/python -B
# -*- coding: utf-8 -*-

import fcntl
import sys
import os
import signal
import argparse
import time

import pygame
import pygame.gfxdraw

from threading import Event

from components.canreader import CanReader
from components.messages import *
from components.megagui import MegaGUI
from components.flukegui import FlukeGUI

screen = None
shutdown = Event()


def run(infile, replay_mode, fullscreen, use_mega):
	global shutdown

	objects = [Msg_1a6(), Msg_2a6(), Msg_3a6(), Msg_4a6()]

	c = CanReader(objects, infile, shutdown, replay_mode)
	c.start()

	if use_mega:
		gui = MegaGUI(objects, shutdown, fullscreen)
	else:
		gui = FlukeGUI(objects, shutdown, fullscreen)

	gui.start()

	while not shutdown.is_set():
		time.sleep(0.1)

	c.join()
	gui.join()


def exit_handler(sig, frame):
	global shutdown
	print("Caught Ctrl-C, will exit")
	shutdown.set()
	pygame.mouse.set_visible(True)
	sys.exit(1)


if __name__ == "__main__":
	signal.signal(signal.SIGINT, exit_handler)

	parser = argparse.ArgumentParser(description='Process CAN data')
	parser.add_argument('-r', '--replay', dest='run_replay', action='store_true',
						help='Run in replay mode, default false')
	parser.add_argument('-f', '--fullscreen', dest='use_fullscreen', action='store_true',
						help='Run in fullscreen mode, default false')
	parser.add_argument('-m', dest='use_mega', action='store_true',
						help='Use the mega GUI, default false')

	args = parser.parse_args()

	# make stdin a non-blocking file
	fd = sys.stdin.fileno()
	fl = fcntl.fcntl(fd, fcntl.F_GETFL)
	fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

	run(sys.stdin, args.run_replay, args.use_fullscreen, args.use_mega)
