#!/usr/bin/python -B
# -*- coding: utf-8 -*-

import sys
import os
import signal
import argparse
import time
import pygame
from pygame.locals import *

try:
	from evdev import InputDevice, list_devices
except:
	print("Could not find 'evdev'. Install with 'sudo apt install python3-evdev'")
	sys.exit(1)

from threading import Event


shutdown = Event()

def run(infile):
	global shutdown


	print(list_devices())
	devices = map(InputDevice, list_devices())
	eventX=""
	for dev in devices:
		print("Found device:", dev.name)
		if dev.name == "ADS7846 Touchscreen":
			eventX = dev.fn

	print("Settled for device:", eventX)

	os.environ["SDL_FBDEV"] = "/dev/fb1"
	os.environ["SDL_MOUSEDRV"] = "TSLIB"
	os.environ["SDL_MOUSEDEV"] = eventX

	pygame.init()
	pygame.mixer.quit()

	# set up the window
	screen = pygame.display.set_mode((320, 240), 0, 32)
	pygame.display.set_caption('Drawing')

	# set up the colors
	BLACK = (  0,   0,   0)
	WHITE = (255, 255, 255)
	RED   = (255,   0,   0)
	GREEN = (  0, 255,   0)
	BLUE  = (  0,   0, 255)
	CYAN  = (  0, 255, 255)
	MAGENTA=(255,   0, 255)
	YELLOW =(255, 255,   0)

	# Fill background
	background = pygame.Surface(screen.get_size())
	background = background.convert()
	background.fill(WHITE)
	box = pygame.draw.rect(background, YELLOW,(40, 0, 40, 240))
	box = pygame.draw.rect(background,  CYAN, (80, 0, 40, 240))
	box = pygame.draw.rect(background, GREEN, (120, 0, 40, 240))
	box = pygame.draw.rect(background,MAGENTA,(160, 0, 40, 240))
	box = pygame.draw.rect(background, RED,   (200, 0, 40, 240))
	box = pygame.draw.rect(background, BLUE  ,(240, 0, 40, 240))
	box = pygame.draw.rect(background, BLACK ,(280, 0, 40, 240))

	# Display some text
	font = pygame.font.Font(None, 36)
	text = font.render("Touch here to quit", 1, (BLACK))
	#text = pygame.transform.rotate(text,270)
	textpos = text.get_rect(centerx=background.get_width()/2,centery=background.get_height()/2)
	background.blit(text, textpos)

	screen.blit(background, (0, 0))
	pygame.display.flip()


	while not shutdown.is_set():
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
				running = False
			elif event.type == pygame.MOUSEBUTTONDOWN:
				print("Pos: %sx%s\n" % pygame.mouse.get_pos())
				if textpos.collidepoint(pygame.mouse.get_pos()):
					pygame.quit()
					sys.exit()
					running = False
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				running = False
		pygame.display.update()
		time.sleep(0.1)
	
	pygame.quit()

def exit_handler(sig, frame):
	global shutdown
	print("Caught Ctrl-C, will exit")
	shutdown.set()


if __name__ == "__main__":
	signal.signal(signal.SIGINT, exit_handler)

	parser = argparse.ArgumentParser(description='Check Touchscreen')

	args = parser.parse_args()

	run(sys.stdin)

