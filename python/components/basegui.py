#!/usr/bin/python -B
# -*- coding: utf-8 -*-

import threading
import pygame
import scipy as sc
import numpy


class BaseGUI(threading.Thread):
	#DEFAULT_FONT = "Noto Mono"

	def __init__(self, objects, shutdown, fullscreen):
		super().__init__()
		size = (800, 480)

		self.objects = objects
		self.shutdown = shutdown
		self.fullscreen = fullscreen

		if fullscreen:
			self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
			self.set_mouse_visible(False)
		else:
			self.screen = pygame.display.set_mode(size)
			self.set_mouse_visible(True)

		# Set header (useful for testing, not so much for full screen mode!)
		pygame.display.set_caption("Curtis Controller Instrument Cluster")

		# Stop keys repeating (not so necessary for this script, but useful if you want to capture other key presses)
		pygame.key.set_repeat()

		pygame.init()
		pygame.mixer.quit()

	def toggle_mouse_visible(self):
		self.mouse_visible = not self.mouse_visible
		pygame.mouse.set_visible(self.mouse_visible)

	def set_mouse_visible(self, visible):
		self.mouse_visible = visible
		pygame.mouse.set_visible(self.mouse_visible)

	@staticmethod
	def fill_gradient(surface, color, gradient, rect=None, vertical=True, forward=True):
		"""fill a surface with a gradient pattern
		Parameters:
		color -> starting color
		gradient -> final color
		rect -> area to fill; default is surface's rect
		vertical -> True=vertical; False=horizontal
		forward -> True=forward; False=reverse

		Pygame recipe: http://www.pygame.org/wiki/GradientCode
		"""
		if rect is None:
			rect = surface.get_rect()

		x1, x2 = rect.left, rect.right
		y1, y2 = rect.top, rect.bottom

		if vertical:
			h = y2 - y1
		else:
			h = x2 - x1
		if forward:
			a, b = color, gradient
		else:
			b, a = color, gradient

		rate = (
			float(b[0] - a[0]) / h,
			float(b[1] - a[1]) / h,
			float(b[2] - a[2]) / h
		)

		fn_line = pygame.draw.line

		if vertical:
			for line in range(y1, y2):
				color = (
					min(max(a[0] + (rate[0] * (line - y1)), 0), 255),
					min(max(a[1] + (rate[1] * (line - y1)), 0), 255),
					min(max(a[2] + (rate[2] * (line - y1)), 0), 255)
				)
				fn_line(surface, color, (x1, line), (x2, line))
		else:
			for col in range(x1, x2):
				color = (
					min(max(a[0] + (rate[0] * (col - x1)), 0), 255),
					min(max(a[1] + (rate[1] * (col - x1)), 0), 255),
					min(max(a[2] + (rate[2] * (col - x1)), 0), 255)
				)
				fn_line(surface, color, (col, y1), (col, y2))

	@staticmethod
	def draw_text(scr, text, size, pos, font, color=(255, 255, 255), topright=False):

		tfont = pygame.font.SysFont(font, size)
		#tfont = pygame.freetype.Font(font, size)
		#tfont.kerning = True
		text_bitmap = tfont.render(text, 1, color)
		if topright:
			rect = text_bitmap.get_rect()
			rect.topright = pos
			pos = rect

		scr.blit(text_bitmap, pos)

	@staticmethod
	def draw_shadow_text(scr, text, size, pos, font, color=(255, 255, 255), topright=False):
		tfont = pygame.font.SysFont(font, size)

		drop_color = (100, 100, 100)
		dropshadow_offset = size // 20

		text_bitmap = tfont.render(text, True, drop_color)
		if topright:
			rect = text_bitmap.get_rect()
			rect.topright = pos
			pos = rect

		scr.blit(text_bitmap, (pos[0] + dropshadow_offset, pos[1] + dropshadow_offset))

		text_bitmap = tfont.render(text, 1, color)
		scr.blit(text_bitmap, pos)

	@staticmethod
	def rotate(points: numpy.core.multiarray, center: numpy.core.multiarray, radians: float) -> numpy.core.multiarray:
		return sc.dot(points - center, sc.array([[sc.cos(radians), sc.sin(radians)], [-sc.sin(radians), sc.cos(radians)]])) + center

