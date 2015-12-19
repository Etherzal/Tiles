'''
Messages handler.
'''

#imports
from Tiles.Logs.Logger import Logger
from Engine.Packet import Packet
from Tiles.Configuration.Tile import Tile
from time import time
from string import *
from random import *

class Message(object):
	"""docstring for Message"""
	def __init__(self):
		super(Message, self).__init__()

	def SendMessage(self, socket, message=False):
		penguin = self._penguins[socket]

		if not penguin.muted:
			if message == False:
				message = str(Packet.Data[3])
			else:
				message = str(message)

			penguin.room.send("%xt%sm%{0}%{1}%{2}%".format(penguin.internalId, penguin.id, message))

