#!/usr/bin/python -B
# -*- coding: utf-8 -*-

import sys
import signal
import argparse
import re
import datetime as dt
import time
import struct

import pygame
import pygame.gfxdraw

import scipy as sc
from threading import Thread

screen = None

tsparser = re.compile(r"\(([0-9]*.[0-9]*)\)")
	


class Msg_1a6(object):
	
	def __init__(self):
		
		self.motor_rms_current = 0
		self.actual_speed = 0
		self.battery_current = 0
		self.dc_capacitor_voltage = 0
		
	def parse(self, data):
				
		self.motor_rms_current = parse_unsigned_int(data, 0, 16)/10.0
		self. actual_speed = parse_signed_int(data, 16, 16)
		self.battery_current = parse_signed_int(data, 32, 16)/10.0		
		self.dc_capacitor_voltage = (parse_unsigned_int(data, 48, 16)/64.0)

	def __str__(self):
		s1 = "           RMS Current: % .01f" % (self.motor_rms_current)
		s2 = "          Actual Speed: % 3d" % (self.actual_speed)
		s3 = "       Battery Current: % .01f" % (self.battery_current)
		s4 = "  DC Capacitor Voltage: % .01f" % (self.dc_capacitor_voltage)
		
		return "\n".join([s1, s2, s3, s4])

class Msg_2a6(object):
	
	def __init__(self):
		
		self.motor_temp = 0
		self.controller_temp = 0
		self.sstate = "N/A"
		self.status = 0
		self.motor_power = 0
		
	def parse(self, data):
		
		self.motor_temp = parse_signed_int(data, 0, 16)/10.0
		self.controller_temp = parse_signed_int(data, 16, 16)/10.0

		state = parse_unsigned_int(data, 32, 8)
		if state == 0:
			self.sstate = "Open"
		elif state == 1:
			self.sstate = "Precharge"
		elif state == 2:
			self.sstate = "Weld Check"
		elif state == 3:
			self.sstate = "Closing Delay"
		elif state == 4:
			self.sstate = "Missing Check"
		elif state == 5:
			self.sstate = "Closed (When Main Enable = On)"
		elif state == 6:
			self.sstate = "Delay"
		elif state == 7:
			self.sstate = "Arc Check"
		elif state == 8:
			self.sstate = "Open Delay"
		elif state == 9:
			self.sstate = "Fault"
		elif state == 10:
			self.sstate = "Closed (When Main Enable = Off)"
		else:
			self.sstate = "Unknown State! " + str(state)

		self.status = parse_unsigned_int(data, 40, 8)		
		self.motor_power = parse_signed_int(data, 48, 16)

	def __str__(self):
		s1 = "     Motor Temperature: % .01f" % (self.motor_temp)
		s2 = "Controller Temperature: % .01f" % (self.controller_temp)
		s3 = "                 State:  %s" % (self.sstate)
		s4 = "                Status: % d" % (self.status)
		s5 = "           Motor Power: % d" % (self.motor_power)
		
		return "\n".join([s1, s2, s3, s4, s5])

class Msg_3a6(object):
	
	def __init__(self):
		
		self.error_code = 0
		self.vehicle_acc = 0
		self.odometer = 0
		
	def parse(self, data):
		
		self.error_code = parse_unsigned_int(data, 0, 8)
		self.vehicle_acc = parse_signed_int(data, 16, 16)/1000.0
		self.odometer = parse_unsigned_int(data, 32, 32)/10.0

	def __str__(self):
		s1 = "            Error Code: % d" % (self.error_code)
		s2 = "  Vehicle Acceleration: % .03f" % (self.vehicle_acc)
		s3 = "              Odometer: % .01f" % (self.odometer)
		
		return "\n".join([s1, s2, s3])

class Msg_4a6(object):
	
	def __init__(self):
		
		self.tts_1 = 0
		self.tts_2 = 0
		
	def parse(self, data):
		
		self.tts_1 = parse_unsigned_int(data, 0, 16)
		self.tts_2 = parse_signed_int(data, 16, 16)

	def __str__(self):
		s1 = "       Time to Speed 1: % d" % (self.tts_1)
		s2 = "       Time to Speed 2: % d" % (self.tts_2)
		
		return "\n".join([s1, s2])

def get_timestamp(s):
	m = tsparser.match(s)
	return float(m.group(1))


def parse_unsigned_int(data, start, length):
	sbyte = int(start/4)
	ebyte = int(sbyte + length/4)
	
	# Extract field from string
	svalue = data[sbyte:ebyte]
	
	# Pair-wise reverse ascii bytes
	nvalue = "".join(reversed([svalue[i:i+2] for i in range(0, len(svalue), 2)]))
	
	ivalue = int(nvalue, 16)
	
	return ivalue

def parse_signed_int(data, start, length):
	unsigned = parse_unsigned_int(data, start, length)
	
	packed = struct.pack('H', unsigned)
	signed_val = struct.unpack('h', packed)[0]
	
	return signed_val
	
def parse_can_data(objects, data):
	
	sbytes = data.split("#")
	
	if data.startswith("1A6"):
		m1a6 = objects[0]
		m1a6.parse(sbytes[1])
		print(m1a6)
		return m1a6
		
	elif data.startswith("2A6"): 
		m2a6 = objects[1]
		m2a6.parse(sbytes[1])
		print(m2a6)
		return m2a6
		
	elif data.startswith("3A6"): 
		m3a6 = objects[2]
		m3a6.parse(sbytes[1])
		print(m3a6)
		return m3a6
		
	elif data.startswith("4A6"): 
		m4a6 = objects[3]
		m4a6.parse(sbytes[1])
		print(m4a6)
		return m4a6

	elif data.startswith("726"): 
		print("")
		print("---------------------------")
		print("")
	else:
		print("UNKNOWN CAN DATA")

	return None
	
def setup_screen(fullscreen):
	
	size = (800,480)

	screen = None
	if fullscreen:
		screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
	else:
		screen = pygame.display.set_mode(size)

	# Set header (useful for testing, not so much for full screen mode!)
	pygame.display.set_caption("Curtis Controller Instrument Cluster")

	# Stop keys repeating (not so necessary for this script, but useful if you want to capture other key presses)
	pygame.key.set_repeat()

	return screen
	
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
	if rect is None: rect = surface.get_rect()
	x1,x2 = rect.left, rect.right
	y1,y2 = rect.top, rect.bottom
	if vertical: h = y2-y1
	else:        h = x2-x1
	if forward: a, b = color, gradient
	else:       b, a = color, gradient
	rate = (
		float(b[0]-a[0])/h,
		float(b[1]-a[1])/h,
		float(b[2]-a[2])/h
	)
	fn_line = pygame.draw.line
	if vertical:
		for line in range(y1,y2):
			color = (
				min(max(a[0]+(rate[0]*(line-y1)),0),255),
				min(max(a[1]+(rate[1]*(line-y1)),0),255),
				min(max(a[2]+(rate[2]*(line-y1)),0),255)
			)
			fn_line(surface, color, (x1,line), (x2,line))
	else:
		for col in range(x1,x2):
			color = (
				min(max(a[0]+(rate[0]*(col-x1)),0),255),
				min(max(a[1]+(rate[1]*(col-x1)),0),255),
				min(max(a[2]+(rate[2]*(col-x1)),0),255)
			)
			fn_line(surface, color, (col,y1), (col,y2))

def draw_shadow_text(scr, text, size, pos):

	tfont = pygame.font.SysFont(None, size)

	text_color = (255, 255, 255)
	drop_color = (100, 100, 100)
	dropshadow_offset = size // 25

	text_bitmap = tfont.render(text, True, drop_color)
	scr.blit(text_bitmap, (pos[0]+dropshadow_offset, pos[1]+dropshadow_offset) )

	text_bitmap = tfont.render(text, 1, text_color)
	scr.blit(text_bitmap, pos )

def rotate(points, center, radians):
    return sc.dot(points - center, sc.array([[sc.cos(radians), sc.sin(radians)], [-sc.sin(radians), sc.cos(radians)]])) + center

def drawGauge(scr, x, y, r, label, value):
	
	line_color = (230,230,230)
	bg_color = (0,0,0)
	line_width = 2
	
	if value < 0.0:
		value = 0.0
	
	# Draw the gauge background and outline
	pygame.gfxdraw.aacircle(scr, x, y, r+line_width, bg_color)
	pygame.gfxdraw.filled_circle(scr, x, y, r+line_width, bg_color)
	pygame.gfxdraw.aacircle(scr, x, y, r, line_color)
	pygame.gfxdraw.filled_circle(scr, x, y, r, line_color)
	pygame.gfxdraw.aacircle(scr, x, y, r-line_width, bg_color)
	pygame.gfxdraw.filled_circle(scr, x, y, r-line_width, bg_color)

	# Draw label in the gauge
	tfont = pygame.font.SysFont(None, int(r/2.5))
	bitmap = tfont.render(label, 1, (255,255,255))
	textpos = bitmap.get_rect()
	textpos.centerx = x
	textpos.centery = y + r/2
	scr.blit(bitmap, textpos )
	
	# Rotate needle	
	ang = 4.5*sc.pi/4.0 - value*(5.0*sc.pi/4.0)
	triag = sc.array([[x,y-2], [x+r-5, y], [x,y+2]])
	triag = rotate(triag, sc.array([x, y]), -ang)
	
	# Draw needle
	triag = [ (int(x), int(y)) for (x,y) in triag ]
	pygame.gfxdraw.aatrigon(scr, triag[0][0], triag[0][1], triag[1][0], triag[1][1], triag[2][0], triag[2][1], (255,0,0))
	pygame.gfxdraw.filled_trigon(scr, triag[0][0], triag[0][1], triag[1][0], triag[1][1], triag[2][0], triag[2][1], (255,0,0))

	# Draw needle center
	pygame.gfxdraw.aacircle(scr, x, y, 3, line_color)
	pygame.gfxdraw.filled_circle(scr, x, y, 3, line_color)
	


def drawBattery(scr, fill_ratio):
	
	color_outline = (255, 255, 255)
	if fill_ratio < 0.2:
		color_fill = (255, 0, 0)
	else:
		color_fill = (255, 255, 255)
		
	x = 50
	y = 330
	width = 50
	height = 100
	line_width = 2
	
	spacing = 1
	
	# Draw battery outline
	pygame.draw.rect(scr, color_outline, [x, y, width, height], line_width)
	
	# Draw battery knob
	pygame.draw.rect(scr, color_outline, [x + (width/2) - 4*line_width, y - (4*line_width), 8*line_width, 4*line_width], line_width)
	 
	# Draw battery fill level
	loffset = spacing + line_width
	roffset = spacing + 2*line_width
	fill_max_height = (height - roffset)
	fill_height = fill_max_height*fill_ratio
	fill_width = width - roffset
	
	pygame.draw.rect(scr, color_fill, [x + loffset, y + loffset + fill_max_height*(1.0 - fill_ratio), fill_width, fill_height])

	
def drawRPM(scr, rpm):

	fill_gradient(scr, (75, 75, 75), (0,0,0) )

	# Figure out position by rendering ...
	myfont = pygame.font.SysFont(None, 100)
	valuelbl = myfont.render(rpm, 1, (255,255,255))
	textpos = valuelbl.get_rect()
	textpos.bottomright = (scr.get_rect().centerx, scr.get_rect().centery)
	
	unitpos =  (textpos[0] + textpos[2] + 10, textpos[1] + textpos[3] - 55) # A bit of trial and error to position the seconds

	
	draw_shadow_text(scr, rpm, 100, textpos.topleft)
	draw_shadow_text(scr, "RPM", 50, unitpos)
	
	# Update the display (i.e. show the output of the above!)
	#pygame.display.flip()

def run_can(infile, replay_mode, objects):
	prev_time = -1
	for line in infile:
		# Remove endings and ignore empty/comment rows
		l = line.strip()
		if len(l) == 0 or l.startswith("#") or not l.startswith("("):
			print("Unparsable line:", l)
			continue
		
		# Split out <TIMESTAMP> <BUS-ID> <DATA>
		row = l.split(" ")
		
		if replay_mode and prev_time == -1:
			prev_time = get_timestamp(row[0])
		
		parse_can_data(objects, row[2])

		timestamp = get_timestamp(row[0])

		# Slow down iteration if in replay mode
		if replay_mode:
			sleeptime = timestamp - prev_time
			time.sleep(sleeptime)
		
		prev_time = timestamp
		
		
def run(infile, replay_mode, fullscreen):
	
	shutdown = False
	screen = setup_screen(fullscreen)
	pygame.init()
	
	objects = [Msg_1a6(), Msg_2a6(), Msg_3a6(), Msg_4a6()]

	t = Thread(target=run_can, args=(infile, replay_mode, objects, ))
	t.start()

	while not shutdown:
		drawRPM(screen, str(objects[0].actual_speed))
		drawBattery(screen, objects[0].dc_capacitor_voltage/170.0)
		drawGauge(screen, 300, 390, 40, "A - RMS", objects[0].motor_rms_current/200.0)
		drawGauge(screen, 400, 390, 40, "kW", objects[1].motor_power/70.0)
		drawGauge(screen, 500, 390, 40, "A - Battery", objects[0].battery_current/200.0)
		
		pygame.display.flip()

		# Check screen events
		for event in pygame.event.get():

			# Handle quit message received
			if event.type == pygame.QUIT:
				exit_handler(None, None)

			# 'Q' to quit    
			if (event.type == pygame.KEYUP): 
				if (event.key == pygame.K_q):
					exit_handler(None, None)

		time.sleep(0.1)

def exit_handler(sig, frame):
	print("Caught Ctrl-C, will exit")
	sys.exit(1)

if __name__ == "__main__":
	
	signal.signal(signal.SIGINT, exit_handler)
	

	parser = argparse.ArgumentParser(description='Process CAN data')
	parser.add_argument('-r', '--replay', dest='run_replay', action='store_true', help='Run in replay mode, default false')
	parser.add_argument('-f', '--fullscreen', dest='use_fullscreen', action='store_true', help='Run in fullscreen mode, default false')

	args = parser.parse_args()
	
	run(sys.stdin, args.run_replay, args.use_fullscreen)
