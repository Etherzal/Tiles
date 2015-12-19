'''
 Main Core handler for Tiles..
'''

#import
from Engine.Receiver import TCPReceiver
from Tiles.Logs.Logger import Logger
from Tiles.DatabaseManager import Manager
from Engine.Packet import Packet
from Tiles.Hashing import Encrypt as Generator
from string import *
from random import *

class Tile(TCPReceiver):

	worldHandlers = dict()
	xmlHandlers = {
		"Policy" : "handlePolicyRequest",
		"verChk" : "handleAPIVersionCheck",
		"rndK"	 : "handleGenerateRandomKey",
		"login"	 : "handleLoginProcess"
	}

	def __init__(self, loadPlugins=False, pluginPath="Tiles/Configuration/Plugins/"):		
		Logger().info("Tile Instance Created!")

		super(Tile, self).__init__()

		self.databaseManager = Manager()

	def handlePolicyRequest(self, socket):
		penguin = self._penguins[socket]

		if penguin.handShake == '':
			port = join(self.ports, ",")
			penguin.send("<cross-domain-policy><allow-access-from domain='*' to-ports='"+port+"' /></cross-domain-policy>")

		return self.loseConnection(socket, "Default Exit!")

	def handleAPIVersionCheck(self, socket):
		penguin = self._penguins[socket]

		verCheck = Packet.Data[0].get("v")

		if verCheck == '153':
			penguin.send("<msg t='sys'><body action='apiOK' r='0'></body></msg>")
			penguin.handShake = 'VersionCheck#{PASSED}'

			return
		else:
			penguin.send("<msg t='sys'><body action='apiKO' r='0'></body></msg>")
			penguin.handShake = "VersionCheck#{FAILED}"

			self.loseConnection(socket)
			return

	def handleGenerateRandomKey(self, socket):
		penguin = self._penguins[socket]

		if penguin.handShake == "VersionCheck#{PASSED}":
			rndKey = Generator().randomKey()
			penguin.randomKey = rndKey
			del rndKey

			penguin.send("<msg t='sys'><body action='rndK' r='-1'><k>" + str(penguin.randomKey) + "</k></body></msg>")
			penguin.handShake = "randomKey#{SENT}"
			return 
		
		else:
			return self.loseConnection(socket)


	def handleXMLPacket(self, socket):
		penguin = self._penguins[socket]

		XMLData = Packet.instance

		if XMLData.Handler in self.xmlHandlers:
			handlerCallback = self.xmlHandlers[XMLData.Handler]

			if hasattr(self, handlerCallback):
				getattr(self, handlerCallback)(socket)
			else:
				Logger().warn("Callback `{0}` for `{1}` doesn't exist!".format(handlerCallback, XMLData.Handler))

		else:
			Logger().warn("Handler for `{0}` doesn't exist!<a>".format(XMLData.Handler))

	def handleWorldPacket(self, socket):
		penguin = self._penguins[socket]

		exceptionList = ["p#getdigcooldown", 'j#js']
		if not str(Packet.Handler) in exceptionList and not penguin.authenticated:
			self.loseConnection(socket, "Un-Authenticated Packet!")

		if penguin.authenticated and str(Packet.Handler) != "p#getdigcooldown":
			Category = Packet.Category

			if Category in self.worldHandlers:
				Packet_Handler, Packet_Extension = str(Packet.Handler).split("#")
				
				if Packet_Handler in self.worldHandlers[Category]:
					if Packet_Extension in self.worldHandlers[Category][Packet_Handler]:
						handlerCallback = self.worldHandlers[Category][Packet_Handler][Packet_Extension]

						if hasattr(self, handlerCallback):
							getattr(self, handlerCallback)(socket)
						else:
							Logger().warn("Attribute `%s` doesn't exists!" % handlerCallback)

					else:
						Logger().warn("Packet extension `%s` for `%s` aint handled!" % (Packet_Extension, Packet_Handler))
				else:
					Logger().warn("Packet handler `%s` for packet `%s` is not handled!" % (Packet_Handler, Packet.Handler))

			else:
				Logger().warn("Category `%s` for packet `%s` doesn't exist!" % (Packet.Category, Packet.rawData))