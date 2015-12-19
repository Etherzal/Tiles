'''
Packet - Both XT and XML Packets Parser for Tiles..
'''

#imports
from lxml.etree import fromstring as decodeXML

class PacketParser(object):
	"""docstring for Packet"""

	instance = None
	PACKET_DELIMITER = "%"
	HANDLED_PACKET_PREFIX = ["xt"]
	WORLD_PREFIX = "xt"

	def __init__(self):
		super(PacketParser, self).__init__()
		self.Data = list()
		self.rawData = str()
		self.Category = str()
		self.Handler = str()
		# Use any one, Currently since XML Packet is used for authentication, move with isXML.
		self.isXT = bool(False)
		self.isXML = bool(False)

	def Parse(self, data):
		data = str(data)
		self.rawData = data

		if data.startswith("<") and data.endswith(">"):
			try:
				XMLdata = decodeXML(data)
			except:
				self.isXT = False
				self.isXML = False
				return False
			finally:
				try:
					self.isXML = True == 1
					self.isXT = True != 1
					if XMLdata.tag == "policy-file-request":
						self.Category = "Request"
						self.Handler = "Policy"
						return True
					elif XMLdata.tag == "msg":
						self.Category = XMLdata.get("t")
						XMLBody = XMLdata.getchildren()[0]
						self.Handler = XMLBody.get("action")

						# Packet checks..
						if self.Category != "sys":
							return False #Not handled
						if self.Handler == "rndk":
							if XMLBody.get("r") != "-1":
								return False # False Statement
						else:
							if self.Handler == "verChk" or self.Handler == "login":
								if XMLBody.get("r") != "0":
									return False # False Statement
							else:
								pass
								#return False # Lets handle this later!!

						self.Data = XMLBody.getchildren()
					else:
						return False # Not handled!!
				except:
					self.Data = list()
					self.rawData = ''
					self.Category = ''
					self.Handler = ''
					self.isXT = False
					self.isXML = False
					return False
				
				finally:
					return True

		elif str(self.PACKET_DELIMITER) in data: # to check if data is delimited
			try:
				self.isXT = True == 1
				self.isXML = True != 1
				PacketArray = data.split(str(self.PACKET_DELIMITER))
				PacketArray.remove("")

				if PacketArray[0] in self.HANDLED_PACKET_PREFIX:
					PacketArray.pop(0)
					self.Category = PacketArray[0]
					self.Handler = PacketArray[1]
					PacketArray.pop(0)
					self.Data = PacketArray

				else:
					return False
			except:
				self.Data = list()
				self.rawData = ''
				self.Category = ''
				self.Handler = ''
				self.isXT = False
				self.isXML = False
				return False

			finally:
				return True

		else:
			return False # Not Handled!!


global Packet
Packet = PacketParser()
Packet.instance = Packet
