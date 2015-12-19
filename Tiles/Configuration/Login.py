'''
PRIMARY LOGIN SERVER FOR Tiles
'''

#imports
from Tiles.Logs.Logger import Logger
from Engine.Packet import Packet
from Tiles.Configuration.Tile import Tile
from Tiles.Hashing import Encrypt
from time import time
from string import *
from random import *

class PrimaryLogin(Tile):
	"""docstring for PrimaryLogin"""
	def __init__(self):
		super(PrimaryLogin, self).__init__()
		Logger().info("Login Server Started!")

	def handleLoginProcess(self, socket):
		penguin = self._penguins[socket]

		self.databaseManager.add(penguin)

		loginXML = Packet.Data[0]
		if loginXML.get("z") != "w1":
			return self.loseConnection(socket, "unhandled login!")

		pengDetails = loginXML.getchildren()
		if pengDetails < 2:
			return self.loseConnection(socket, "Not enough arguments!")

		del pengDetails
		penguinName = loginXML.find("nick").text
		penguinPass = loginXML.find("pword").text

		if penguinName == '' or len(str(penguinName)) < 4 or penguinPass == '':
			penguin.send("%xt%e%-1%101%")
			return self.loseConnection(socket)

		loggedInUsers = list(str(self._penguins[k].username) for k in self._penguins)
		if penguinName in loggedInUsers:
			Logger().warn("Suspecious login, %s" % penguinName)
			return self.loseConnection(socket, "Suspecious login!")
			
		if not penguin.database.username_exists(penguinName):
			penguin.send("%xt%e%-1%101%")
			return self.loseConnection(socket, "Username doesn't exist!")

		Logger().info("New login attempt, %s"%penguinName)

		pengDetails = penguin.database.getColumnsByUsername(penguinName, list(("ID", "Password", "SWID", "Email", "Banned")))
		encryptedPassword = Encrypt().loginEncrypt(pengDetails["Password"], penguin.randomKey)

		if str(penguinPass) != str(encryptedPassword):
			penguin.send("%xt%e%-1%101%")
			return self.loseConnection(socket, "Incorrect Password!")
		else:
			if str(pengDetails["Banned"]).isdigit() or str(pengDetails["Banned"]) == "perm":
				if str(pengDetails["Banned"]) == "perm":
					penguin.send("%xt%e%-1%603%")
					return self.loseConnection(socket, "Banned for-ever!")
				else:
					if int(pengDetails["Banned"]) > time(): #still banned
						ban_hrs = round(int(pengDetails["Banned"]) - time()) / (3600)
						penguin.send("%xt%e%-1%601%{0}%".format(ban_hrs))
						return self.loseConnection(socket)

			confirmationHash = Encrypt().hash(str(Encrypt().randomKey())+penguinName, True)
			friendsKey = confirmationHash[16:] + Encrypt().hash(str(pengDetails["SWID"]), True)[:16]
			loginTime = time()

			penguin.database.updateColumnById(str(int(pengDetails["ID"])), "ConfirmationHash", confirmationHash)
			penguin.database.updateColumnById(str(int(pengDetails["ID"])), "LoginKey", encryptedPassword)

			penguin.handShake = "Login#{Logged}"
			email = pengDetails["Email"][:3] + "**@" + pengDetails["Email"].split("@")[1]
			dbusersInServer = int(penguin.database.getUsersInServer('100')[0])
			usersInServer = round((dbusersInServer) / (5.0))

			penguin.send("%xt%l%-1%{0}|{1}|{2}|{3}|1|45|2|false|true|{4}%{5}%{6}%100,{8}%{7}%".format( str(int(pengDetails['ID'])), pengDetails['SWID'],
				penguinName, encryptedPassword, loginTime, confirmationHash, friendsKey, email, usersInServer))

			return self.loseConnection(socket, "Logged In!")

	def disconnectClient(self, socket):
		penguin = self._penguins[socket]

		self.databaseManager.remove(penguin)