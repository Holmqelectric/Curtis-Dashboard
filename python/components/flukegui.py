#!/usr/bin/python -B
# -*- coding: utf-8 -*-

import time
import os
import math as m

import pygame
import pygame.gfxdraw


from .basegui import BaseGUI

FONT_NAME = "Noto Mono"

class FlukeGUI(BaseGUI):

	def __init__(self, objects, shutdown, fullscreen):
		super(FlukeGUI, self).__init__(objects, shutdown, fullscreen)

	def draw_gauge(self, x, y, r, label, value, unit):

		if value < 1.0:
			value = 0.0

		self.draw_text(self.screen, label, 10, (x-30, y-10), color=(180, 180, 180))
		self.draw_text(self.screen, "%.01f" % value, 15, (x, y), topright=True)
		self.draw_text(self.screen, unit, 15, (x+10, y))

	def draw_battery(self):

		image_index = int((self.objects[0].dc_capacitor_voltage / 150.0)*5) + 1

		imagefile = "battery_%d.png" % image_index
		segment = pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'images', imagefile))
		segment = segment.convert_alpha()
		self.screen.blit(segment, (0,0))


	def draw_power(self):

		power = max(self.objects[1].motor_power, 0)
		needle = pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'images', 'kw_needle.png'))
		needle = needle.convert_alpha()
		needle = pygame.transform.rotozoom(needle, -power*(160.0/70.0), 1.0)
		pos = needle.get_rect()
		pos.centerx = 503
		pos.centery = 189
		self.screen.blit(needle, pos)

	def draw_speed(self):

		speed = self.objects[0].get_speed()
		needle = pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'images', 'speed_needle.png'))
		needle = needle.convert_alpha()
		needle = pygame.transform.rotozoom(needle, -speed*(180.0/160.0), 1.0)
		pos = needle.get_rect()
		pos.centerx = 399
		pos.centery = 187
		self.screen.blit(needle, pos)

	def draw_background(self):
		bg = pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'images', 'background.png'))
		bg = bg.convert_alpha()
		bg = pygame.transform.scale(bg, (800, 480))
		self.screen.blit(bg, (0,0))

	def load_full_image(self, filename):
			img = pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'images', filename))
			img = img.convert_alpha()
			self.screen.blit(img, (0, 0))

	def set_highbeam(self, state):
		if state:
			self.load_full_image('high_beam.png')

	def set_turn_left(self, state):
		if state:
			self.load_full_image('left_turn.png')

	def set_turn_right(self, state):
		if state:
			self.load_full_image('right_turn.png')

	def set_warning_signal(self, state):
		if state:
			self.load_full_image('warn_signal.png')

	def print_rpm(self):
		rpm = max(self.objects[0].actual_speed, 0)
		self.draw_text(self.screen, str(rpm), 60, (20, 217))

	def print_power(self):
		power = max(self.objects[1].motor_power, 0)
		self.draw_text(self.screen, str(power), 60, (20, 325))

	def print_current(self):
		current = max(self.objects[0].motor_rms_current, 0)
		self.draw_text(self.screen, str(current), 60, (20, 107))

	def print_battery_voltage(self):
		voltage = max(self.objects[0].dc_capacitor_voltage, 0)
		self.draw_text(self.screen, "%.0f" % voltage, 30, (590, 109))

	def print_range(self):
		range = max(self.objects[2].odometer, 0)
		self.draw_text(self.screen, "%.0f" % range, 60, (635, 322), topright=True)

	def print_odometer(self):
		odometer = max(self.objects[2].odometer, 0)
		self.draw_text(self.screen, "%.0f" % odometer, 45, (754, 430), topright=True)

	def print_ctrl_temp(self):
		temp = max(self.objects[1].controller_temp, 0)
		self.draw_text(self.screen, "%.0f" % temp, 45, (527, 430), topright=True)

	def print_motor_temp(self):
		temp = max(self.objects[1].motor_temp, 0)
		self.draw_text(self.screen, "%.0f" % temp, 45, (304, 430), topright=True)

	def run(self):
		count = 0
		while not self.shutdown.is_set():
			self.draw_background()
			self.draw_speed()
			self.draw_battery()
			self.draw_power()
			self.set_highbeam(count%10==0)
			self.set_turn_left(count%10==2)
			self.set_turn_right(count%10==4)
			self.set_warning_signal(count%10==6)

			self.print_rpm()
			self.print_power()
			self.print_current()
			self.print_battery_voltage()
			self.print_range()
			self.print_odometer()
			self.print_ctrl_temp()
			self.print_motor_temp()

			count += 1

			pygame.display.flip()

			# Check screen events
			for event in pygame.event.get():

				# Handle quit message received
				if event.type == pygame.QUIT:
					self.shutdown.set()
				# 'Q' to quit
				if (event.type == pygame.KEYUP):
					if (event.key == pygame.K_q):
						self.shutdown.set()

			time.sleep(0.1)
