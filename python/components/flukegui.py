#!/usr/bin/python -B
# -*- coding: utf-8 -*-

import time
import os

import pygame
import pygame.gfxdraw

from components.settings import DashboardSettings as DS

from .basegui import BaseGUI

if DS.DEBUG:
	from components.dummy_pi import GPIO


FONT_NAME = "Noto Mono"
IMAGE_DIR = "images-fluke"

class FlukeGUI(BaseGUI):

	def __init__(self, states, event_handler, shutdown, fullscreen):
		super(FlukeGUI, self).__init__(states, shutdown, fullscreen)

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
		for index in range(1,7):
			imagefile = "battery_%d.png" % index
			segment = pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', IMAGE_DIR, imagefile))
			self.bsegments.append(segment.convert_alpha())

		self.powerneedle = pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', IMAGE_DIR, 'kw_needle.png'))
		self.powerneedle = self.powerneedle.convert_alpha()

		self.speedneedle = pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', IMAGE_DIR, 'speed_needle.png'))
		self.speedneedle = self.speedneedle.convert_alpha()

		self.bg = pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', IMAGE_DIR, 'background.png'))
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

		soc = self.states.get_soc_percent()
		image_index = int(soc * 6)

		if image_index > 5:
			image_index = 5

		if image_index < 0:
			return

		self.screen.blit(self.bsegments[image_index], (0,0))


	def draw_power(self):

		power = self.states.get_motor_power()
		needle = pygame.transform.rotozoom(self.powerneedle, -power*(160.0/70.0), 1.0)
		pos = needle.get_rect()
		pos.centerx = 503
		pos.centery = 189
		self.screen.blit(needle, pos)

	def draw_speed(self):

		speed = self.states.get_speed()
		needle = pygame.transform.rotozoom(self.speedneedle, -speed*(180.0/160.0), 1.0)
		pos = needle.get_rect()
		pos.centerx = 399
		pos.centery = 187
		self.screen.blit(needle, pos)

	def draw_background(self):
		self.screen.blit(self.bg, (0,0))

	@staticmethod
	def load_image(filename):
		img = pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', IMAGE_DIR, filename))
		img = img.convert_alpha()
		return img

	def draw_text(self, scr, text, size, pos, font=FONT_NAME, color=(255, 255, 255), topright=False):
		super(FlukeGUI, self).draw_text(scr, text, size, pos, font, color, topright)


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
		rpm = self.states.get_actual_speed()
		self.draw_text(self.screen, str(rpm), 60, (20, 217))

	def print_power(self):
		power = self.states.get_motor_power()
		self.draw_text(self.screen, "%.01f" % power, 60, (20, 325))

	def print_current(self):
		current = self.states.get_motor_rms_current()
		self.draw_text(self.screen, str(current), 60, (20, 107))

	def print_battery_voltage(self):
		voltage = self.states.get_dc_capacitor_voltage()
		self.draw_text(self.screen, "%.0f" % voltage, 30, (590, 109))

	def print_range(self):
		range = self.states.get_odometer()
		self.draw_text(self.screen, "%.0f" % range, 60, (635, 322), topright=True)

	def print_odometer(self):
		odometer = self.states.get_odometer()
		self.draw_text(self.screen, "%.0f" % odometer, 45, (754, 430), topright=True)

	def print_ctrl_temp(self):
		temp = self.states.get_controller_temp()
		self.draw_text(self.screen, "%.0f" % temp, 45, (527, 430), topright=True)

	def print_motor_temp(self):
		temp = self.states.get_motor_temp()
		self.draw_text(self.screen, "%.0f" % temp, 45, (304, 430), topright=True)

	def print_dcdc(self):
		dcdc = self.states.get_dcdc()
		self.draw_text(self.screen, "%.01f" % dcdc, 45, (120, 430), topright=True)


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
			#self.print_range()
			self.print_odometer()
			self.print_ctrl_temp()
			self.print_motor_temp()
			self.print_dcdc()

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

				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_l and DS.DEBUG:
						GPIO.output(DS.TURN_LEFT_IN_PCB_PIN, GPIO.HIGH)

				if event.type == pygame.KEYUP:
					if event.key == pygame.K_q:
						self.shutdown.set()

					if event.key == pygame.K_m:
						self.toggle_mouse_visible()

					if event.key == pygame.K_l and DS.DEBUG:
						GPIO.output(DS.TURN_LEFT_IN_PCB_PIN, GPIO.LOW)


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
		pygame.quit()


