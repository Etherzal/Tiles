'''
Server.py - This contains the basic fundamendal structure for the whole server.
'''

#imports
from socket import *
from select import select # Select is an basic and important module required for powerful socket connection

#classes
class TCPServer(object):
	
	"""
	docstring for TCPServer
	- This class initiates the Server configuration,
	and Managing IP and Ports of the server handled in it.
	"""

	delimiter = '\n' # Default delimiter
	clients = {} # Clients/Connected sockets and classes (socket:class) are listed in a Dictionary for easier use

	connections = list() # Sockets/Client-socket currently connected to the server

	maxclients = 500 # Default Max number of clients able to connect to server

	__MainSocket = None # Literally a Master socket.

	maxbytes = 8192
	ports = list()

	def __init__(self, backlog=5, errormode=True):
		super(TCPServer, self).__init__()

		# Alternate way to set the configuration.
		self.backlog = int(backlog)	
		self.errormode = bool(errormode)

	def __handleAcceptClients(self):
		# Accept any new socket/client connection, connecting to the server
		acceptedSocket = self.__MainSocket.accept()
		client = acceptedSocket[0] # [0] is the socket ;)
		
		# set custom client options
		client.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		client.setblocking(0) #no blocking mode

		#add it to connected clients
		self.connections.append(client)

		return client

	def __listenToAddress(self, ip, port):
		# Trial and error method to print out error at last if any!
		error = None
		errorMsg = ''
		ip = str(ip)
		port = int(port)

		try:
			self.__MainSocket.bind((ip, port))
			#self.connections.append( tuple((ip, port)) )
		except Exception, msg:
			error = True
			errorMsg = str(msg)

		if self.errormode and error:
			raise Exception("Caught Exception in private function listenToAddress: "+errorMsg)	

		return error == None

	def init(self, address, maxclients=500, delimiter=None):
		# Another type of configuring
		self.maxclients = maxclients
		if delimiter:
			self.delimiter = delimiter

		if not self.__MainSocket:
			self.__MainSocket = socket(AF_INET, SOCK_STREAM, SOL_TCP)
			self.__MainSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # Reuse same IP for different ports.
			self.__MainSocket.setblocking(0) # Non Blocking Server

		if isinstance(address, list):
			for connection in address:
				ip, port = connection
				self.ports.append(str(port))
				listened = self.__listenToAddress(ip, port)
				if not listened:
					# don't move on further!
					break

		elif isinstance(address, tuple):
			ip, port = address
			self.ports.append(str(port))
			listened = self.__listenToAddress(ip, port)
			if not listened:
				return

		else:
			if self.errormode:
				raise TypeError("Type `%s` for variable 'address' is not handled!" % (str(type(address))))
			return

		self.__MainSocket.listen(self.backlog)

	def run(self, time_out=None):
		while 1:
			sockets = [self.__MainSocket] + self.connections
			try:
				readable, writable, errored = select(sockets, [], [], 5) # Selecting the current available clients 
				#																   An important thing for non-blocking server
			except timeout:
				continue
			except Exception, e:
				print 'Exception in Selecting available sockets: '+ str(e)
				continue

			# readable = Available clients..

			if len(readable) == 0:
				continue

			for socket in readable:
				if socket == self.__MainSocket:
					client = self.__handleAcceptClients()
					# User's custom handle for any new accepted clients
					self.ConnectionMade(client)
				
				else:
					exceptionMessage = 'Unknwon Exception'

					try:
						buffer = socket.recv(self.maxbytes)
					except Exception, e:
						exceptionMessage = str(e)
						buffer = False

					if not buffer:
						self.HandleDisconnectClient(socket, exceptionMessage)
						self._RemoveSocket(socket)
						continue
					else:
						self.DataReceived(socket, buffer)

	def _RemoveSocket(self, socket):
		if socket in self.connections:
			self.connections.remove(socket)

		socket.close()
