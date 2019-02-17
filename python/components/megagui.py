#!/usr/bin/python -B
# -*- coding: utf-8 -*-

import os
import time

import pygame
import pygame.gfxdraw

import scipy as sc

from .basegui import BaseGUI

FONT_NAME = "Noto Mono"

class MegaGUI(BaseGUI):

	def __init__(self, objects, evh, shutdown, fullscreen):
		super(MegaGUI, self).__init__(objects, shutdown, fullscreen)

	def draw_gauge(self, x, y, r, label, value):

		line_color = (230, 230, 230)
		bg_color = (0, 0, 0)
		line_width = 2

		if value < 0.0:
			value = 0.0

		# Draw the gauge background and outline
		pygame.gfxdraw.aacircle(self.screen, x, y, r + line_width, bg_color)
		pygame.gfxdraw.filled_circle(self.screen, x, y, r + line_width, bg_color)
		pygame.gfxdraw.aacircle(self.screen, x, y, r, line_color)
		pygame.gfxdraw.filled_circle(self.screen, x, y, r, line_color)
		pygame.gfxdraw.aacircle(self.screen, x, y, r - line_width, bg_color)
		pygame.gfxdraw.filled_circle(self.screen, x, y, r - line_width, bg_color)

		# Draw label in the gauge
		tfont = pygame.font.SysFont(FONT_NAME, int(r / 4))
		bitmap = tfont.render(label, 1, (255, 255, 255))
		textpos = bitmap.get_rect()
		textpos.centerx = x
		textpos.centery = y + r / 2
		self.screen.blit(bitmap, textpos)

		# Rotate needle
		ang = 4.5 * sc.pi / 4.0 - value * (5.0 * sc.pi / 4.0)
		triag = sc.array([[x, y - 2], [x + r - 5, y], [x, y + 2]])
		triag = self.rotate(triag, sc.array([x, y]), -ang)

		# Draw needle
		triag = [(int(x), int(y)) for (x, y) in triag]

		x1, y1 = triag[0]
		x2, y2 = triag[1]
		x3, y3 = triag[2]

		# Draw triangle needle, first anti-alias and then fill
		pygame.gfxdraw.aatrigon(self.screen, x1, y1, x2, y2, x3, y3, (255, 0, 0))
		pygame.gfxdraw.filled_trigon(self.screen, x1, y1, x2, y2, x3, y3, (255, 0, 0))
		# Draw shadow
		pygame.gfxdraw.aapolygon(self.screen, [(x2, y2), (x1, y1), (x2, y2)], (100, 100, 100))

		# Draw needle center
		pygame.gfxdraw.aacircle(self.screen, x, y, 3, line_color)
		pygame.gfxdraw.filled_circle(self.screen, x, y, 3, line_color)

		# Load lens
		lens = pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'images', 'ring2.png'))
		lens = lens.convert_alpha()
		# lens = pygame.transform.scale(lens, (2*(r-line_width), 2*(r-line_width)))
		lens = pygame.transform.scale(lens, (2 * (r), 2 * (r)))
		self.screen.blit(lens, (x - r, y - r))

	def draw_battery(self):

		fill_ratio = self.objects[0].dc_capacitor_voltage / 170.0

		color_outline = (255, 255, 255)
		if fill_ratio < 0.2:
			color_fill = (255, 0, 0)
		else:
			color_fill = (255, 255, 255)

		x = 50
		y = 50
		width = 70
		height = 380
		line_width = 2

		spacing = 1

		# Draw battery outline
		pygame.draw.rect(self.screen, color_outline, [x, y, width, height], line_width)

		# Draw battery knob
		pygame.draw.rect(self.screen, color_outline,
			[x + (width / 2) - 4*line_width, y - (4*line_width), 8*line_width, 4*line_width], line_width)

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

		self.fill_gradient(self.screen, (50, 50, 50), (0, 0, 0))

		self.draw_shadow_text(self.screen, "%.0f" % speed, 100, FONT_NAME, (510, 120), True)
		self.draw_shadow_text(self.screen, "km/h", 50, FONT_NAME, (520, 150))

	def run(self):
		while not self.shutdown.is_set():
			self.draw_speed()
			self.draw_battery()
			self.draw_gauge(240, 330, 40, "°C Ctrl", self.objects[1].controller_temp / 200.0)
			self.draw_gauge(340, 330, 40, "A RMS", self.objects[0].motor_rms_current / 200.0)
			self.draw_gauge(460, 330, 60, "kW", self.objects[1].motor_power / 70.0)
			self.draw_gauge(580, 330, 40, "A Batt", self.objects[0].battery_current / 200.0)
			self.draw_gauge(680, 330, 40, "°C Motor", self.objects[1].motor_temp / 200.0)

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
