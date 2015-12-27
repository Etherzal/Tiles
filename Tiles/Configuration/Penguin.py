'''
Penguins - Create a new Penguin instance for any newly joined client to CPPS Server for it's private stuffs!!
'''

# imports
#basic stuffs
from Tiles.Logs.Logger import Logger
from Engine.Packet import Packet
from time import time
from string import *
from random import *
import hashlib

class Penguin(object):
	"""docstring for Penguin"""

	internalId = '-1'

	authenticated = False
	username, password, randomKey = '', '', ''
	color, head, face, neck, body, hand, feet, photo, flag = '0', '0', '0', '0', '0', '0', '0', '0', '0'

	age = None
	avatar = '0'
	avatarAttributes = ''
	coins = '0'

	inventory = list()
	careInventory = list()
	activeIgloo = ''

	furniture, locations, floors, igloos = dict(), dict(), dict(), dict()

	moderator = False
	muted = False

	membershipDays = 0

	frame, x, y = 0, 0, 0

	room = None
	puffleQuest = dict()

	database = None
	handShake = ''

	# for further security
	IP = '::1'

	def __init__(self, socket, delimiter):
		self.delimiter = delimiter
		self.socket = socket

		self.IP = self.socket.getpeername()

	def LoadPlayer(self):
		myDetails = self.database.getColumnsById(self.id, ["Color", "Head", "Face", "Neck", "Body", "Hand", "Feet", "Photo", "Flag", "Walking",
			"Avatar", "AvatarAttributes", "RegistrationDate", "Moderator", "Inventory", "CareInventory", "Coins", 
			"Furniture", "Floors", "Igloos", "Locations"])
		if len(str(myDetails["Furniture"])) != 0:
			for furn in str(myDetails["Furniture"]).split(","):
				furnDetails = furn.split("|")
				self.furniture[furnDetails[0]] = list((furnDetails[1], furnDetails[2]))

		if len(str(myDetails["Floors"])) != 0:
			for floor in str(myDetails["Floors"]).split(","):
				floorDetails = floor.split("|")
				self.floors[floorDetails[0]] = floorDetails[1]

		if len(str(myDetails["Igloos"])) != 0:
			for igloo in str(myDetails["Igloos"]).split(","):
				self.igloos[igloo[0]] = igloo[1]

		if len(str(myDetails["Locations"])) != 0:
			for location in str(myDetails["Locations"]).split(","):
				locationDetails = location.split("|")
				self.locations[locationDetails[0]] = locationDetails[1]

		self.color, self.head, self.face, self.neck, self.body, self.hand, self.feet, self.photo, self.flag = myDetails["Color"], \
			myDetails["Head"], myDetails["Face"], myDetails["Neck"], myDetails["Body"], myDetails['Hand'], myDetails["Feet"], \
			myDetails['Photo'], myDetails["Flag"]

		self.age = float(time()-int(myDetails["RegistrationDate"])/86400)

		self.membershipDays = (31*7) + (30*5) # A Month prob

		self.avatar = myDetails['Avatar']
		self.avatarAttributes = myDetails['AvatarAttributes']

		self.coins = myDetails['Coins']
		self.moderator = bool(int(myDetails['Moderator']) > 0)

		self.inventory = myDetails['Inventory'].split("%")

	def getPlayerString(self):
		player = [
			str(self.id),
			str(self.username),
			str(45),
			str(self.color),
			str(self.head),
			str(self.face),
			str(self.neck),
			str(self.body),
			str(self.hand),
			str(self.feet),
			str(self.flag),
			str(self.photo),
			str(self.x),
			str(self.y),
			str(self.frame),
			str(1),
			str(self.membershipDays),
			str(self.avatar),
			str(0),
			str(self.avatarAttributes)
			] #Burp!

		#You have to implement Walking puffle details!!

		return "|".join(player)

	def sendWorldPacket(self, *packets):
		int_id = str(self.internalId)
		packs = list([str(k) for k in packets])
		if len(packs) < 1:
			packs += [""]
		packs = list([packs[0], int_id] + list(packs[1:]))

		packetArray = list(("", str(Packet.WORLD_PREFIX))) + packs + [""]
		packet = join(packetArray, str(Packet.PACKET_DELIMITER))

		self.send(packet)

	def send(self, buffer):
		Logger().debug("OUTGOING: "+str(buffer))
		
		buffer = str(buffer)
		buffer += self.delimiter

		try:
			self.socket.send(buffer)
		except:
			pass # Sometimes error may raise!!
