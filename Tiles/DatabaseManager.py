'''
Database manager, manages the DB Object between joined penguins.. Defaut - 30 Penguins per Object
'''

#imports
from Tiles.Database import Database

class Manager(object):
	"""docstring for DatabaseManager"""
	def __init__(self):
		super(Manager, self).__init__()
		self.DBConnections = [] # Currently available Database Objects
		self.DBPenguins = {} # No of penguins in Available Databases, ie, if `n`s DB Obj's index is `i`, then self.DBPenguins[i] = array of penguins using that DB.

	def add(self, penguin):
		if len(self.DBConnections) == 0:
			DBIndex = self.__createDB()
			if DBIndex not in self.DBPenguins:	self.DBPenguins[DBIndex] = []
			self.DBPenguins[DBIndex].append(penguin)

		else:
			DBIndex = self.__getOpenDatabase()
			if DBIndex not in self.DBPenguins: self.DBPenguins[DBIndex] = []
			self.DBPenguins[DBIndex].append(penguin)

		penguin.database = self.DBConnections[DBIndex]

		return DBIndex

	def remove(self, penguin):
		for DBindex in self.DBPenguins:
			if penguin in self.DBPenguins[DBindex]:
				index = self.DBPenguins[DBindex].index(penguin)
				del self.DBPenguins[DBindex][index]
				if len(self.DBPenguins[DBindex]) == 0: 
					del self.DBPenguins[DBindex]
					del self.DBConnections[DBindex]
				break

	def __getOpenDatabase(self):
		found = False
		DBindex = None
		for DBindex in self.DBPenguins:
			if len(self.DBPenguins[DBindex]) < 30:
				found = True
				DBindex = DBindex
				break
		
		if found: return DBindex
		else:
			return self.__createDB()

	def __createDB(self):
		newDB = Database()
		self.DBConnections.append(newDB)
		index = self.DBConnections.index(newDB)

		return index