'''
Player - Categ, Packets Handler!
'''

#imports
from Tiles.Logs.Logger import Logger
from Engine.Packet import Packet
from Tiles.Configuration.Tile import Tile
from time import time
from string import *
from random import *
from datetime import datetime

class Player(object):
	"""docstring for Player"""
	def __init__(self):
		super(Player, self).__init__()

	def GetLastRevision(self, socket):
		penguin = self._penguins[socket]

		revmonth = 9
		revdate = 2
		now =  datetime(2015, revmonth, revdate, 12, 34, 8)
		y = now.strftime('%Y')
		m = now.strftime('%m')
		d = now.strftime('%d')

		penguin.send("%xt%glr%-1%{0}{1}{2}%".format(m,d,y[-2:]))

	def GetPlayerById(self, socket):
		penguin = self._penguins[socket]

		req_id = Packet.Data[2]
		if penguin.database.id_exists(req_id):
			req_info = penguin.database.getColumnsById(penguin.id, list(("Username", "SWID")))

			penguin.sendWorldPacket("pbi", req_info["SWID"], req_id, req_info["Username"])

	def SendPlayerMove(self, socket):
		penguin = self._penguins[socket]

		penguin.x, penguin.y = Packet.Data[2:4]

		penguin.sendWorldPacket("sp", penguin.id, penguin.x, penguin.y)

	def SendPlayerFrame(self, socket):
		penguin = self._penguins[socket]

		penguin.frame = Packet.Data[2]

		penguin.sendWorldPacket("sf", penguin.id, penguin.frame)

	def PlayerHeartBeat(self, socket):
		penguin = self._penguins[socket]

		penguin.sendWorldPacket("h")

	def SendAction(self, socket):
		penguin = self._penguins[socket]

		action = Packet.Data[2]

		penguin.sendWorldPacket("sa", penguin.id, action)

	def GetABTestData(self, socket):
		pass # Custom Handled

	def SendEmote(self, socket):
		penguin = self._penguins[socket]

		emote_id = str(Packet.Data[2])
		if emote_id.isdigit():
			penguin.sendWorldPacket("se", penguin.id, emote_id)

	def SendSnowBall(self, socket):
		penguin = self._penguins[socket]

		x, y = Packet.Data[2:4]

		penguin.sendWorldPacket("sb", penguin.id, x, y)

	def PlayerBySWIDUsername(self, socket):
		penguin = self._penguins[penguin]

		swid = Packet.Data[2]

		username = penguin.database.getColumnByIdentifier("SWID", swid, "Username", "penguins")

		penguin.sendWorldPacket("pbsu", username)

	def SendSafeMessage(self, socket):
		penguin = self._penguins[penguin]

		ssmsg = Packet.Data[2]
		if ssmsg.isdigit():
			penguin.room.send("%xt%ss%{0}%{1}%{2}%".format(penguin.room.internalId, penguin.id, ssmsg))

	def GetPlayerByName(self, socket):
		penguin = self._penguins[socket]

		name = Packet.Data[2]
		if penguin.database.username_exists(name):
			details = penguin.getColumnByUsername(name, ["SWID", "ID"])
			penguin.sendWorldPacket("pbn", details["SWID"], details["ID"], name)

	def GetPlayer(self, socket):
		penguin = self._penguins[socket]

		req_id = Packet.Data[2]
		if penguin.database.id_exists(req_id):
			details = penguin.getColumnsById(req_id, ["Username", "Color", "Head", "Face", "Neck", "Body", "Hand", "Feet", "Flag", "Photo"])
			array = [str(k) for k in (details["Username"], "45", details["Color"], details["Head"], details["Face"], details["Neck"],  \
				details["Body"], details["Hand"], details["Feet"], details["Flag"], details["Photo"])]

			penguin.sendWorldPacket("gp", req_id, array)