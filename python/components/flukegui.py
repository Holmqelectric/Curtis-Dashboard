#!/usr/bin/python -B
# -*- coding: utf-8 -*-

import time
import os

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

		fill_ratio = self.objects[0].dc_capacitor_voltage / 170.0

		color_outline = (255, 255, 255)
		if fill_ratio < 0.2:
			color_fill = (255, 0, 0)
		else:
			color_fill = (255, 255, 255)

		x = 683
		y = 90
		width = 100
		height = 240
		line_width = 2

		spacing = 1

		# Draw battery fill level
		loffset = spacing + line_width
		roffset = spacing + 2 * line_width
		fill_max_height = (height - roffset)
		fill_height = fill_max_height * fill_ratio
		fill_width = width - roffset

		pygame.draw.rect(self.screen, color_fill,
				[x + loffset, y + loffset + fill_max_height * (1.0 - fill_ratio), fill_width, fill_height])

	def draw_speed(self):

		speed = self.objects[0].get_speed()

		self.draw_shadow_text(self.screen, "%.0f" % speed, 100, FONT_NAME, (480, 120), True)

	def draw_background(self):
		bg = pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'images', 'background.png'))
		bg = bg.convert_alpha()
		bg = pygame.transform.scale(bg, (800, 480))
		self.screen.blit(bg, (0,0))

	def run(self):
		while not self.shutdown.is_set():
			self.draw_background()
			self.draw_speed()
			self.draw_battery()
			self.draw_gauge(240, 380, 40, "Ctrl. Temp", self.objects[1].controller_temp, "°C")
			self.draw_gauge(340, 380, 40, "RMS Amps", self.objects[0].motor_rms_current, "A")
			self.draw_gauge(460, 380, 60, "Power", self.objects[1].motor_power, "kW")
			self.draw_gauge(580, 380, 40, "Batt. Amps", self.objects[0].battery_current, "A")
			self.draw_gauge(680, 380, 40, "Motor Temp", self.objects[1].motor_temp, "°C")

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
