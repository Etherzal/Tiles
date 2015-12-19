'''
Items Handler
'''

#imports
from Tiles.Logs.Logger import Logger
from Engine.Packet import Packet
from Tiles.Configuration.Tile import Tile
from time import time
from string import *
from random import *

class Item(object):
	"""docstring for Item"""
	def __init__(self):
		super(Item, self).__init__()

	def GetPlayerInventory(self, socket):
		penguin = self._penguins[socket]

		penguin.sendWorldPacket("gi", join(penguin.inventory, "%"))
