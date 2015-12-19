'''
Load Crumbs to the Server!!
'''

#imports
from Tiles.Logs.Logger import Logger
from Tiles.Configuration.Server.Rooms import Room
from time import time
from string import *
from random import *
from urllib2 import urlopen
import os
from json import loads

class Crumbs(object):

	items = dict()
	pins = list()
	locations = dict()
	furniture = dict()
	floors = dict()
	igloos = dict()
	rooms = dict()

	def __init__(self):		
		super(Crumbs, self).__init__()		

	def __loadItems(self, wrapper):
		for item in wrapper:
			item_id = item["paper_item_id"]
			self.items[item_id] = item["cost"]

			if str(item["type"]) == "8":
				self.pins += [item_id]

			# Again here if it is an EPF Item, ie item['is_epf'] exists, add it to your EPF Array

	def __loadRooms(self, wrapper):
		for externalRoomId in wrapper:
			aboutRoom = wrapper[externalRoomId]
			self.rooms[str(externalRoomId)] = Room(str(externalRoomId), len(self.rooms)+1, aboutRoom["name"], aboutRoom["max_users"],
				aboutRoom["path"]=="")

	def __loadFurnitures(self, wrapper):
		for furniture in wrapper:
			furnitureId = furniture["furniture_item_id"]

			self.furniture[furnitureId] = furniture["cost"]

	def __loadFloors(self, wrapper):
		for floor in wrapper:
			floorId = floor["igloo_floor_id"]

			self.floors[floorId] = floor["cost"]

	def __loadLocations(self, wrapper):
		for location in wrapper:
			locationId = location["igloo_location_id"]

			self.locations[locationId] = location["cost"]

	def __loadIgloos(self, wrapper):
		for iglooId in wrapper:
			iglooDetails = wrapper[iglooId]

			self.igloos[iglooId] = iglooDetails["cost"]

	def FetchGame_configs(self, jsonFile):
		jsonFile = str(jsonFile).lstrip("/").rstrip("/")
		game_configs_url = str("http://media1.clubpenguin.com/play/en/web_service/game_configs/")
		jsonFile_game_configs_url = game_configs_url + jsonFile

		jsonFilePath = str("Tiles/Crumbs/") + jsonFile
		if not os.path.isfile(jsonFilePath):
			jsonBuffer = urlopen(jsonFile_game_configs_url).read()
			with open(jsonFilePath, "w") as file: file.write(jsonBuffer)

		file = open(jsonFilePath, "r")
		jsonFile_Data = file.read()
		jsonFile_Data = loads(jsonFile_Data)

		return jsonFile_Data

	def loadCrumbs(self):
		# First check for crumbs.
		# Then load it.

		if not os.path.exists("Tiles/Crumbs"):
			os.makedirs("Tiles/Crumbs")

		rooms = self.FetchGame_configs("rooms.json")
		self.__loadRooms(rooms)

		paper_items = self.FetchGame_configs("paper_items.json")
		self.__loadItems(paper_items)

		locations = self.FetchGame_configs("igloo_locations.json")
		self.__loadLocations(locations)

		furnitures = self.FetchGame_configs("furniture_items.json")
		self.__loadFurnitures(furnitures)

		floors = self.FetchGame_configs("igloo_floors.json")
		self.__loadFloors(floors)

		igloos = self.FetchGame_configs("igloos.json")
		self.__loadIgloos(igloos)