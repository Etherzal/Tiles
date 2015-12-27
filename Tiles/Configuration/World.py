'''
Main Configuration for The WHOLE PLAYABLE Server.. TileServer
'''

#imports
from Tiles.Logs.Logger import Logger
from Engine.Packet import Packet
from Tiles.Configuration.Tile import Tile
from Tiles.Hashing import Encrypt
from time import time
from string import *
from random import *

from Tiles.Configuration.Crumbs.Crumb import Crumbs
from Tiles.Configuration.Handlers.Play.Navigation import Navigation
from Tiles.Configuration.Handlers.Entertainment import SStudio
from Tiles.Configuration.Handlers.Play import Messaging, items, Player, Settings

class TileServer(Tile, Crumbs, Navigation, Messaging.Message, Player.Player, Settings.Settings, SStudio.SStudio):

	worldHandlers = {
		# Categories
		"s" : {
			#Navigation
			"j" : {
				"js" 	: "JoinServer",
				"jr" 	: "JoinRoom",
				"jp" 	: "JoinPlayer",
				"grs"	: "GoRefreshServer"
			},
			#Items
			"i" : {
				"gi"	: "GetPlayerInventory",
				"qpp"	: "GetPlayerPins",
				"qpa"	: "GetPlayerAwards"
			},
			#Player
			"u" : {
				"glr"	: "GetLastRevision",
				"pbi"	: "GetPlayerById",
				"sp"	: "SendPlayerMove",
				"sf"	: "SendPlayerFrame",
				"h" 	: "PlayerHeartBeat",
				"sa"	: "SendAction",
				"gabcms": "GetABTestData",
				"se"	: "SendEmote",
				"sb"	: "SendSnowBall",
				"pbsu"	: "PlayerBySWIDUsername",
				"ss"	: "SendSafeMessage",
				"pbn"	: "GetPlayerByName",
				"gp"	: "GetPlayer",
			},
			#Settings
			"s" : {
				"upc"	: "UpdatePlayerColor",
				"uph"	: "UpdatePlayerHead",
				"upf"	: "UpdatePlayerFace",
				"upn"	: "UpdatePlayerNeck",
				"upb"	: "UpdatePlayerBody",
				"upa"	: "UpdatePlayerHand",
				"upe"	: "UpdatePlayerFeet",
				"upp"	: "UpdatePlayerPhoto",
				"upl"	: "UpdatePlayerFlag"
			},
			#Messaging
			"m" : {
				"sm"	: "SendMessage"
			},
			#Sound Studio
			"musictrack" : {
				"getsharedmusictracks" 		: 'GetMySharedTracks',
				"getmymusictracks"	  		: 'FetchMyMusicTracks',
				"savemymusictrack"	  		: 'SaveMyMusic',
				"deletetrack"		  		: 'DeleteMyMusic',
				"loadmusictrack"			: 'LoadMusicByTrack',
				"sharemymusictrack"	  		: "ShareTrack",
				"broadcastingmusictracks"	: "BroadcastMusic",
				"refreshmytracklikes"		: "RefreshMusicLikes",
				"liketrack"					: "LikePlayerTrack",
				"canliketrack"				: "CanLikeMyTrack"
			},
			"p" : {
				"checkpufflename" : "checkname"
			}
		}
	}

	def __init__(self):
		super(TileServer, self).__init__()
		self.loadCrumbs()

		Logger().info("World Instance Created!")
		self.init_sstudio()

	def checkname(self, socket):
		penguin = self._penguins[socket]
		if not Packet.Data[2].isdigit():
			penguin.sendWorldPacket("checkpufflename", Packet.Data[2], "1")
		else:
			penguin.sendWorldPacket("checkpufflename", Packet.Data[2], "-1")

	def handleLoginProcess(self, socket):
		penguin = self._penguins[socket]
		self.databaseManager.add(penguin)

		loginXML = Packet.Data[0]
		if loginXML.get("z") != "w1":
			return self.loseConnection(socket, "unhandled login!")

		peng_details = loginXML.getchildren()
		if peng_details < 2:
			return self.loseConnection(socket, "Not enough arguments!")

		del peng_details
		penguin_infos = loginXML.find("nick").text
		penguin_pass = loginXML.find("pword").text

		if penguin_infos == '' or penguin_pass == '' or len(str(penguin_infos).split("|")) < 10:
			penguin.send("%xt%e%-1%101%")
			return self.loseConnection(socket, "Wrong parameters")
		
		loggedInUsers = list(str(self._penguins[k].username) for k in self._penguins)
		if str(penguin_infos).split("|")[2] in loggedInUsers:
			Logger().warn("Suspecious login, %s" % penguin.username)
			return self.loseConnection(socket, "Suspecious login!")
		penguin.username, penguin.swid, penguin.id = str(penguin_infos).split("|")[2], str(penguin_infos).split("|")[1], str(penguin_infos).split("|")[0]

		

		if not penguin.database.username_exists(penguin.username):
			penguin.send("%xt%e%-1%101%")
			return self.loseConnection(socket, "Username doesn't exists!")

		if not penguin.database.id_exists(penguin.id):
			penguin.send("%xt%e%-1%101%")
			return self.loseConnection(socket, "ID Doesn't exists!")

		dbPengDetails = penguin.database.getColumnsById(penguin.id, list(("Username", "SWID", "ConfirmationHash", "LoginKey")))
		worldLoginKey = Encrypt().hash(dbPengDetails["LoginKey"]+penguin.randomKey, True) + dbPengDetails["LoginKey"]
		if not str(penguin_infos).split("|")[3] == dbPengDetails["LoginKey"]:
			penguin.send("%xt%e%-1%101%")
			return self.loseConnection(socket, "Incorrect Password!!")

		penguinWorldLoginKey, pengConfirmationHash = str(penguin_pass).split("#")

		penguin.database.updateColumnById(penguin.id, "ConfirmationHash", str(hash(penguin.username)))

		if str(dbPengDetails["ConfirmationHash"]) != str(pengConfirmationHash):
			penguin.send("%xt%e%-1%101%")
			return self.loseConnection(socket, "Wrong Confirmation Hash!")
		elif str(worldLoginKey) != str(penguinWorldLoginKey):
			penguin.send("%xt%e%-1%101%")
			return self.loseConnection(socket, "Wrong Login Key!")
		else:
			penguin.authenticated = True
			penguin.send("%xt%l%-1%#loggedIn%")

			return 

	def disconnectClient(self, socket):
		penguin = self._penguins[socket]

		self.databaseManager.remove(penguin)