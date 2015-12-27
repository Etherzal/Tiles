'''
Database Object for whlole Tiles Server..
'''

#imports
from MySQLdb.connections import Connection
from MySQLdb.cursors import *
from lxml.etree import fromstring
from string import *
from Tiles.Logs.Logger import Logger

class Eagle(object):

	MySQL_Delimiter = ";"

	__CurrentCursor = Cursor
	__StrCursor = "Cursor"

	def __init__(self, Query, ss):
		self.__Erite = ss
		self.__Query = str(Query)
		if self.__Query == '':
			raise Exception("Cannot execute or bind to empty query")
		else:
			self.__Query += self.MySQL_Delimiter
			self.__Queries = self.__Query.split(self.MySQL_Delimiter)
			self.__Queries.remove("")

	def delimit(self, delimiter):
		self.MySQL_Delimiter = delimiter

	def bindValue(self, From, to):
		for Qindex in range(len(self.__Queries)):
			Query = self.__Queries[Qindex]
			Queries = Query.split(" ")
			for Q in Queries:
				Qr = Q.replace("'", "").replace('"', "")
				if str(Qr) == str(From):
					iQ = Queries.index(Q)
					Queries[iQ] = "'%s'" % to

			self.__Queries[Qindex] = " ".join(Queries)

		self.__Query = self.MySQL_Delimiter.join(self.__Queries)

	def execute(self, cursr=None):
		if cursr == None:
			__Cursor = self.__CurrentCursor(self.__Erite)
		else:
			__Cursor = cursr(self.__Erite)

		__Cursor.execute(self.__Query)
		
		return __Cursor

class Database(Connection):

	def __init__(self, **config):
		with open('Database.xml', "r") as DBFile:
			DBXMLData = fromstring(DBFile.read())

		__MySQL_User = DBXMLData.find("user").text
		__MySQL_pass = DBXMLData.find("pass").text
		__MySQL_pass = '' if __MySQL_pass is None else __MySQL_pass
		__MySQL_host = DBXMLData.find("host").text
		__MySQL_db   = DBXMLData.find("dbname").text
		# Start database -> connection; Connect ::
		try:
			super(Database, self).__init__(host=__MySQL_host, user=__MySQL_User, passwd=__MySQL_pass, db=__MySQL_db, port=3306)
		except Exception, e:
			raise Exception("Cannot connect to given credentials, check MySQL and infos given!"+str(e))

		self.autocommit(True)

	def prepare(self, query):
		return Eagle(query, self)

	def username_exists(self, username):
		ColumnQuery = self.prepare("SELECT `ID` from `penguins` WHERE `Username` = :user")
		ColumnQuery.bindValue(":user", username)
		ColumnValue = ColumnQuery.execute()

		exists = len(ColumnValue.fetchall()) != 0

		return exists

	def id_exists(self, id):
		ColumnQuery = self.prepare("SELECT `ID` from `penguins` WHERE `ID` = :id")
		ColumnQuery.bindValue(":id", id)
		ColumnValue = ColumnQuery.execute()

		exists = len(ColumnValue.fetchall()) != 0

		return exists

	def getColumnById(self, id, column):
		ColumnQuery = self.prepare("SELECT `{columns}` FROM `penguins` WHERE `ID` = :id".format(columns=column))
		ColumnQuery.bindValue(":id", str(id))
		ColumnValue = ColumnQuery.execute()

		ColumnValue = ColumnValue.fetchall()[0][0]
		return ColumnValue

	def getColumnsById(self, id, columns):
		column = join(columns, ",")

		ColumnQuery = self.prepare("SELECT {columns} FROM `penguins` WHERE `ID` = :id".format(columns=column))
		ColumnQuery.bindValue(":id", str(id))
		ColumnsValue = ColumnQuery.execute(DictCursor)

		ColumnsValue = ColumnsValue.fetchallDict()[0]
		return ColumnsValue

	def getColumnByUsername(self, username, column):
		ColumnQuery = self.prepare("SELECT `{columns}` FROM `penguins` WHERE `Username` = :user".format(columns=column))
		ColumnQuery.bindValue(":user", str(username))
		ColumnValue = ColumnQuery.execute()

		ColumnValue = ColumnsValue.fetchall()[0][0]
		return ColumnValue

	def getColumnsByUsername(self, username, columns):
		column = join(columns, ", ")

		ColumnQuery = self.prepare("SELECT {columns} FROM `penguins` WHERE `Username` = :user".format(columns=column))
		ColumnQuery.bindValue(":user", str(username))
		ColumnsValue = ColumnQuery.execute(DictCursor)

		ColumnsValue = ColumnsValue.fetchallDict()[0]
		return ColumnsValue

	def updateColumnById(self, id, column, value):
		ColumnQuery = self.prepare("UPDATE `penguins` SET `{column}` = :value WHERE `ID` = :id".format(column=column))
		ColumnQuery.bindValue(":value", value)
		ColumnQuery.bindValue(":id", id)

		ColumnQuery.execute()

	def getUsersInServer(self, serverID):
		ColumnQuery = self.prepare("SELECT `Penguins` FROM `servers` WHERE `ID`= :serv")
		ColumnQuery.bindValue(":serv", serverID)
		ColumnValue = ColumnQuery.execute()

		return ColumnValue.fetchall()[0]

	def updateUsersInServer(self, ID, add=True):
		if add == True:
			Cursor(self).execute('UPDATE `servers` SET `Penguins`= Penguins + 1 WHERE `ID`=\"%s\"'%ID)
		else:
			Cursor(self).execute('UPDATE `servers` SET `Penguins`= Penguins - 1 WHERE `ID`=\"%s\"'%ID)

	def getColumnByIdentifier(self, identify_column, identifier, column, fromTable):
		Query = self.prepare("SELECT `{0}` FROM `{1}` WHERE `{2}` = :identifier".format(column, fromTable, identify_column))
		Query.bindValue(":identifier", identifier)

		return Query.execute().fetchall()[0][0]

	def getAllByIdentifier(self, identify_column, identifier, column, fromTable):
		Query = self.prepare("SELECT {0} FROM `{1}` WHERE `{2}` = :identifier".format(column, fromTable, identify_column))
		Query.bindValue(":identifier", identifier)

		return Query.execute().fetchall()[0]

	def executeMe(self, query):
		Query = self.prepare(query)

		return Query.execute()

	def false(self, *args, **kwargs):
		Logger().error("Error in Tile-Database: "+str(self.errored))
		return False

	def __getattr__(self, attr):
		print attr
		def CallFunc(*args, **kwargs):
			try:
				return getattr(self, attr)(*args, **kwargs)
			except Exception, e:
				self.errored = str(e)
				return self.false

		return CallFunc
