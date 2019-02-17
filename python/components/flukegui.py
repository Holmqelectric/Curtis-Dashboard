#!/usr/bin/python -B
# -*- coding: utf-8 -*-

import time
import os

import pygame
import pygame.gfxdraw

from components.settings import DashboardSettings as DS

from .basegui import BaseGUI

FONT_NAME = "Noto Mono"

class FlukeGUI(BaseGUI):

	def __init__(self, objects, event_handler, shutdown, fullscreen):
		super(FlukeGUI, self).__init__(objects, shutdown, fullscreen)

		self.event_handler = event_handler

		self.turn_left = False
		self.turn_right = False
		self.warning_signal = False
		self.highbeam = False

		self.highbeam_img = self.load_image('high_beam.png')
		self.left_turn_img = self.load_image('left_turn.png')
		self.right_turn_img = self.load_image('right_turn.png')
		self.warning_signal_img = self.load_image('warn_signal.png')

		self.bsegments = []
		for index in range(1,6):
			imagefile = "battery_%d.png" % index
			segment = pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'images', imagefile))
			self.bsegments.append(segment.convert_alpha())

		self.powerneedle = pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'images', 'kw_needle.png'))
		self.powerneedle = self.powerneedle.convert_alpha()

		self.speedneedle = pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'images', 'speed_needle.png'))
		self.speedneedle = self.speedneedle.convert_alpha()

		self.bg = pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'images', 'background.png'))
		self.bg = self.bg.convert_alpha()
		self.bg = pygame.transform.scale(self.bg, (800, 480))

	@staticmethod
	def check_mouse_inside(pos, rect):
		x1 = rect[0][0]
		x2 = rect[2][0]
		y1 = rect[0][1]
		y2 = rect[1][1]

		if x1 <= pos[0] <= x2 and y1 <= pos[1] <= y2:
			return True
		else:
			return False

	def draw_gauge(self, x, y, r, label, value, unit):

		if value < 1.0:
			value = 0.0

		self.draw_text(self.screen, label, 10, (x-30, y-10), color=(180, 180, 180))
		self.draw_text(self.screen, "%.01f" % value, 15, (x, y), topright=True)
		self.draw_text(self.screen, unit, 15, (x+10, y))

	def draw_battery(self):

		image_index = int((self.objects[0].dc_capacitor_voltage / 150.0)*5) + 1
		self.screen.blit(self.bsegments[image_index], (0,0))


	def draw_power(self):

		power = max(self.objects[1].motor_power, 0)
		needle = pygame.transform.rotozoom(self.powerneedle, -power*(160.0/70.0), 1.0)
		pos = needle.get_rect()
		pos.centerx = 503
		pos.centery = 189
		self.screen.blit(needle, pos)

	def draw_speed(self):

		speed = self.objects[0].get_speed()
		needle = pygame.transform.rotozoom(self.speedneedle, -speed*(180.0/160.0), 1.0)
		pos = needle.get_rect()
		pos.centerx = 399
		pos.centery = 187
		self.screen.blit(needle, pos)

	def draw_background(self):
		self.screen.blit(self.bg, (0,0))

	@staticmethod
	def load_image(filename):
		img = pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'images', filename))
		img = img.convert_alpha()
		return img

	def show_full_image(self, img):
		self.screen.blit(img, (0, 0))

	def draw_highbeam(self):
		if self.event_handler.highbeam_active:
			self.show_full_image(self.highbeam_img)

	def draw_turn_left(self):
		if self.event_handler.turn_signal.left_state:
			self.show_full_image(self.left_turn_img)

	def draw_turn_right(self):
		if self.event_handler.turn_signal.right_state:
			self.show_full_image(self.right_turn_img)

	def draw_warning_signal(self):
		if self.event_handler.warning_active:
			self.show_full_image(self.warning_signal_img)

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
		while not self.shutdown.is_set():

			#
			#
			# Draw everything on the screen
			#
			#
			self.draw_background()
			self.draw_speed()
			self.draw_battery()
			self.draw_power()
			self.draw_turn_left()
			self.draw_turn_right()
			self.draw_warning_signal()
			self.draw_highbeam()

			self.print_rpm()
			self.print_power()
			self.print_current()
			self.print_battery_voltage()
			self.print_range()
			self.print_odometer()
			self.print_ctrl_temp()
			self.print_motor_temp()

			pygame.display.flip()

			#
			#
			# Handle screen events
			#
			#

			ev = pygame.event.get()
			for event in ev:

				# Handle quit message received
				if event.type == pygame.QUIT:
					self.shutdown.set()

				# 'Q' to quit
				if event.type == pygame.KEYUP:
					if event.key == pygame.K_q:
						self.shutdown.set()

				# Handle on-screen controls
				if event.type == pygame.MOUSEBUTTONUP:
					pos = pygame.mouse.get_pos()
					if self.check_mouse_inside(pos, DS.LEFT_TURN_BBOX):
						self.event_handler.toggle_left_turn()

					if self.check_mouse_inside(pos, DS.RIGHT_TURN_BBOX):
						self.event_handler.toggle_right_turn()

					if self.check_mouse_inside(pos, DS.WARN_LIGHT_BBOX):
						self.event_handler.toggle_warning()

					if self.check_mouse_inside(pos, DS.HIGHBEAM_BBOX):
						self.event_handler.toggle_highbeam()


			time.sleep(0.1)

		pygame.mouse.set_visible(True)

