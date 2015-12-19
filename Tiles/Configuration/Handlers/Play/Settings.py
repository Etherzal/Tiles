'''
Settings Categ handler..
'''

#imports
from Tiles.Logs.Logger import Logger
from Engine.Packet import Packet
from Tiles.Configuration.Tile import Tile
from time import time
from string import *
from random import *

class Settings(object):
	"""docstring for Settings"""
	def __init__(self):
		super(Settings, self).__init__()

	def UpdatePlayerColor(self, socket):
		penguin = self._penguins[socket]
		item_id  = Packet.Data[2]
		penguin.color = str(item_id)
		penguin.sendWorldPacket("upc", penguin.id, item_id)

	def UpdatePlayerHead(self, socket):
		penguin = self._penguins[socket]
		item_id  = Packet.Data[2]
		penguin.head = str(item_id)
		penguin.sendWorldPacket("uph", penguin.id, item_id)
		
	def UpdatePlayerFace(self, socket):
		penguin = self._penguins[socket]
		item_id  = Packet.Data[2]
		penguin.face = str(item_id)
		penguin.sendWorldPacket("upf", penguin.id, item_id)
		
	def UpdatePlayerNeck(self, socket):
		penguin = self._penguins[socket]
		item_id  = Packet.Data[2]
		penguin.neck = str(item_id)
		penguin.sendWorldPacket("upn", penguin.id, item_id)
		
	def UpdatePlayerBody(self, socket):
		penguin = self._penguins[socket]
		item_id  = Packet.Data[2]
		penguin.body = str(item_id)
		penguin.sendWorldPacket("upb", penguin.id, item_id)
		
	def UpdatePlayerHand(self, socket):
		penguin = self._penguins[socket]
		item_id  = Packet.Data[2]
		penguin.hand = str(item_id)
		penguin.sendWorldPacket("upa", penguin.id, item_id)
		
	def UpdatePlayerFeet(self, socket):
		penguin = self._penguins[socket]
		item_id  = Packet.Data[2]
		penguin.feet = str(item_id)
		penguin.sendWorldPacket("upe", penguin.id, item_id)
		
	def UpdatePlayerPhoto(self, socket):
		penguin = self._penguins[socket]
		item_id  = Packet.Data[2]
		penguin.photo = str(item_id)
		penguin.sendWorldPacket("upp", penguin.id, item_id)
		
	def UpdatePlayerFlag(self, socket):
		penguin = self._penguins[socket]
		item_id  = Packet.Data[2]
		penguin.flag = str(item_id)
		penguin.sendWorldPacket("upl", penguin.id, item_id)

		