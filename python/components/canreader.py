#!/usr/bin/python -B
# -*- coding: utf-8 -*-

import re
import threading
import time


tsparser = re.compile(r"\(([0-9]*.[0-9]*)\)")


class CanReader(threading.Thread):

	def __init__(self, object, infile, shutdown, replay_mode):
		super().__init__()
		self.object = object
		self.infile = infile
		self.shutdown = shutdown
		self.replaymode = replay_mode

	@staticmethod
	def get_timestamp(s):
		m = tsparser.match(s)
		return float(m.group(1))

	def parse_can_data(self, data):
		sbytes = data.split("#")

		if data.startswith("1A6"):
			self.object.parse_m1(sbytes[1])

		elif data.startswith("2A6"):
			self.object.parse_m2(sbytes[1])

		elif data.startswith("3A6"):
			self.object.parse_m3(sbytes[1])

		elif data.startswith("4A6"):
			self.object.parse_m4(sbytes[1])

		elif data.startswith("726"):
			pass
		else:
			print("UNKNOWN CAN DATA")


	def run(self):

		prev_time = -1
		while not self.shutdown.is_set():

			try:
				line = self.infile.readline()
			except:
				time.sleep(0.1)
				continue


			# Remove endings and ignore empty lines
			l = line.strip()
			if len(l) == 0:
				time.sleep(0.1)
				continue

			# Ignore comments
			if l.startswith("#"):
				continue

			# Expect timestamp with '('
			if not l.startswith("("):
				print("Unparsable line:", l)
				continue

			# Split out <TIMESTAMP> <BUS-ID> <DATA>
			row = l.split(" ")

			if self.replaymode and prev_time == -1:
				prev_time = self.get_timestamp(row[0])

			self.parse_can_data(row[2])

			timestamp = self.get_timestamp(row[0])

			# Slow down iteration if in replay mode
			if self.replaymode:
				sleeptime = timestamp - prev_time
				time.sleep(sleeptime)

			prev_time = timestamp
