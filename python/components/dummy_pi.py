



class GPIO(object):
	BOARD = "board"
	IN = "in"
	OUT = "out"
	HIGH = "high"
	LOW = "low"
	__mode = "not set"
	__pins = [(None, None)]*50

	@classmethod
	def setmode(cls, mode):
		cls.__mode = mode

	@classmethod
	def setup(cls, pin, direction):
		cls.__pins[pin] = (direction, None)

	@classmethod
	def output(cls, pin, state):
		current_state = cls.__pins[pin]
		print("Changed pin %d from '%s' to '%s'" % (pin, current_state[1], state))
		cls.__pins[pin] = (cls.__pins[pin][0], state)

	@classmethod
	def cleanup(cls):
		print("Cleaning up")
