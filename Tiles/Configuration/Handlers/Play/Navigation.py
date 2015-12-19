'''
Handles all the Packets of handler "J" ie, "Navigation"
'''

#imports
from Tiles.Logs.Logger import Logger
from Engine.Packet import Packet
from Tiles.Configuration.Tile import Tile
from time import time
from string import *
from random import *

class Navigation(object):

	def __init__(self):
		super(Navigation, self).__init__()

	def joinRoom(self, penguin, roomId, x=0, y=0):
		if not str(roomId) in self.rooms:
			return
		elif penguin.room is not None:
			penguin.room.removePlayer(penguin)

		# self.leaveWaddle(penguin)

		penguin.frame = 1
		penguin.x = x
		penguin.y = y
			
		self.rooms[str(roomId)].addPlayer(penguin)

	def JoinServer(self, socket):
		penguin = self._penguins[socket]

		if str(penguin.id) != Packet.Data[2]:
			penguin.send("%xt%e%-1%101%")
			return self.loseConnection(socket, "Wong ID")

		penguin_login_key = Packet.Data[3]
		if str(penguin_login_key) == "":
			penguin.send("%xt%e%-1%101%")
			return self.loseConnection(socket, "Invalid Login Key!")

		dbLoginKey = penguin.database.getColumnById(penguin.id, "LoginKey")

		penguin.database.updateColumnById(penguin.id, "LoginKey", str(hash(penguin.swid)))

		if str(dbLoginKey) != str(penguin_login_key):
			penguin.send("%xt%e%-1%101%")
			return self.loseConnection(socket, "Wrong Login Key!")

		penguin.LoadPlayer()
		isModerator = bool(penguin.moderator)
		penguin.EPF = dict()
		penguin.EPF["status"], penguin.EPF["points"], penguin.EPF["career"] = penguin.database.getColumnById(penguin.id, "EPF").split(",")

		penguin.send("%xt%js%-1%1%{0}%{1}%1%".format(penguin.EPF['status'], isModerator*1))

		lpString = "{0}|%{1}%0%1440%{2}%{3}%0%7521%%7%1%0%211843".format(penguin.getPlayerString(), penguin.coins, time(), penguin.age)
		penguin.send("%xt%lp%-1%{0}%".format(lpString))

		self.joinRoom(penguin, "100", 0, 0)

	def JoinRoom(self, socket):
		penguin = self._penguins[socket]

		room, x, y = Packet.Data[2:5]
		self.joinRoom(penguin, room, x, y)

	def JoinPlayer(self, socket):
		# Igloo Joining Function!!
		pass

	def GoRefreshServer(self, socket):
		penguin = self._penguins[socket]

		penguin.room.refreshRoom(penguin)