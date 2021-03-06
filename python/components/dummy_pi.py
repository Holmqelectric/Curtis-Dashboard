



class GPIO(object):
	BOARD = "board"
	IN = "in"
	OUT = "out"
	HIGH = "high"
	LOW = "low"
	PUD_DOWN = "PULL DOWN"
	PUD_UP = "PULL UP"
	__mode = "not set"
	__pins = [(None, None)]*50

	@classmethod
	def setmode(cls, mode):
		cls.__mode = mode

	@classmethod
	def setup(cls, pin, direction, pull_up_down=PUD_DOWN):
		if cls.__pins[pin][0] is not None:
			print("WARNING: Pin %d is already setup. Has direction '%s'" % (pin, cls.__pins[pin][0]))
			return

		#cls.__pins[pin] = (direction, GPIO.LOW)
		if pull_up_down == GPIO.PUD_DOWN:
			cls.__pins[pin] = (direction, GPIO.LOW)
		else:
			cls.__pins[pin] = (direction, GPIO.HIGH)

	@classmethod
	def output(cls, pin, state):
		current_state = cls.__pins[pin]
		if current_state[0] != GPIO.OUT:
			print("WARNING: Pin %d is not an output pin." % (pin))
			#return

		print("Changed pin %d from '%s' to '%s'" % (pin, current_state[1], state))
		cls.__pins[pin] = (cls.__pins[pin][0], state)

	@classmethod
	def input(cls, pin):
		if cls.__pins[pin][0] != GPIO.IN:
			print("WARNING: Pin %d is not an input pin." % (pin))
			return None
		#print("Read state '%s' from pin %d" % (cls.__pins[pin][1], pin))
		return cls.__pins[pin][1]

	@classmethod
	def cleanup(cls):
		print("Cleaning up")
