from colorama import init
from colorama import Fore as color
import sys, time

class Logger(object):
	"""docstring for Logger"""

	def __init__ (self):
		init()
		self.format = '[%H:%M:%S]'
		self.time = lambda: time.strftime(self.format)

	def log(self, start, msg, end):
		form = color.LIGHTWHITE_EX
		form+= 'TILE '
		form+= str(self.time()) + ' : '
		form+= color.RESET
		form+= start
		form+= msg
		form+= end
		form+= '\n'
		sys.stdout.write(form)

	def info (self, information):
		self.log(color.LIGHTGREEN_EX, str(information), color.RESET)

	def warn (self, warning):
		self.log(color.LIGHTCYAN_EX, str(warning), color.RESET)

	def error (self, errormsg):
		self.log(color.LIGHTRED_EX, str(errormsg), color.RESET)

	def debug (self, message):
		self.log(color.LIGHTWHITE_EX, str(message), color.RESET)
		