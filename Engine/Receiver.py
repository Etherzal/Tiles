'''
RECEIVER - Obtained from Dote's basic Socket server, with compilation of both Basic and Alternate receiver!!
Create a new penguin instance for any newly joined client!!
'''

#imports
from Engine.Server import TCPServer
from Tiles.Configuration.Penguin import Penguin
from Engine.Packet import Packet
from Tiles.Logs.Logger import Logger

class TCPReceiver(TCPServer):
	"""docstring for TCPReceiver"""

	delimiter = chr(0)

	def __init__(self, backlog=5, errormode=True):
		super(TCPReceiver, self).__init__(backlog, errormode)
		self._penguins = dict()

	def DataReceived(self, client, data):
		Packets = str(data).split(str(self.delimiter))
		Packets.pop()

		for p_data in Packets:
			Logger().debug("RECEIVED: "+str(p_data))
			isPacket = Packet.Parse(p_data)
			if not isPacket:
				self.loseConnection(client, "Malformed packet!")
			else:
				if Packet.isXML:
					try:
						self.handleXMLPacket(client)
					except Exception, e:
						Logger().warn("ERROR IN HANDLING XML PACKET: "+str(e))
				elif Packet.isXT:
					try:
						self.handleWorldPacket(client)
					except Exception, e:
						Logger().warn("ERROR IN HANDLING WORLD PACKET: "+str(e))
				else:
					pass # Let's ignore it now! :P

	def ConnectionMade(self, client):
		Logger().info("New Client. #"+str(len(self._penguins)))
		penguin = Penguin(client, self.delimiter)
		self._penguins[client] = penguin

	def HandleDisconnectClient(self, client, reason):
		Logger().info("Penguin Disconnected!(%s)"%(str(reason)))
		self.disconnectClient(client)
		if client in self._penguins:
			del self._penguins[client]

	def loseConnection(self, client, exception="Lost Connection - Connection aborted by the Server host"):
		self.HandleDisconnectClient(client, exception)
		self._RemoveSocket(client)
	
	#overidden in children
	
	def handleXMLPacket(self, socket):
		pass	
	
	def handleWorldPacket(self, socket):
		pass

	def disconnectClient(self, client):
		pass