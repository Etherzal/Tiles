'''
Rooms Handler for Tiles-Server.
Handle it the other way out!
You can also try new methods too.. But this is not more Pythonic way tho, you can make use of DictClass of Python bulitin too.
'''

#imports
from Tiles.Logs.Logger import Logger
from Engine.Packet import Packet
from string import *
from random import *

class Room(object):

	name = ''
	max_users = 0
	is_game = False
	internalId = 0
	externalId = 0

	penguins = list()


	def __init__(self, external_id, internal_id, name, max_users, isGame):
		self.externalId = str(external_id)
		self.internalId = str(internal_id)
		self.name = str(name)
		self.max_users = str(max_users)
		self.is_game = bool(isGame)

	def addPlayer(self, penguin):
		self.penguins.append(penguin)

		if self.externalId == "999":
			penguin.send("%xt%jx%{0}%{1}%".format(penguin.room.internalId, self.externalId))
		else:
			if self.is_game:
				nonBlackholeGames = ['900', '909', '956', '950', '963', '121']

				if self.externalId in nonBlackholeGames:
					penguin.send("%xt%jnbhg%{0}%{1}%".format(self.internalId, self.externalId))
				else:
					penguin.send("%xt%jg%{0}%{1}%".format(self.internalId, self.externalId))

			else:
				roomString = self.getRoomString()
				penguin.send("%xt%jr%{0}%{1}%{2}%".format(self.internalId, self.externalId, roomString))

				self.send("%xt%ap%{0}%{1}%".format(self.internalId, penguin.getPlayerString()))

		penguin.room = self
		penguin.internalId = self.internalId

	def removePlayer(self, penguin):
		self.penguins.remove(penguin)

		self.send("%xt%rp%{0}%{1}%".format(self.internalId, penguin.id))

	def refreshRoom(self, penguin):
		penguin.send("%xt%grs%-1%{0}%{1}%".format(self.externalId, self.getRoomString()))

	def getRoomString(self):
		roomString = "%".join(map(lambda penguin: penguin.getPlayerString(), self.penguins))
		return roomString

	def send(self, buffer):
		for penguin in self.penguins:
			penguin.send(buffer)