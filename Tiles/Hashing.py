''' 
HASHING - Generate Random Key, Handle Login Hash and Password Hash
'''

#imports
from string import *
from random import *
from hashlib import md5

class Encrypt(object):
	"""docstring for Encrypt"""
	def __init__(self):
		super(Encrypt, self).__init__()

	def randomKey(self):
		Chars = list(uppercase + lowercase + digits + "`~@#$()_+-={}|[]:,.")
		for _ in range(100):
			shuffle(Chars)

		rndK = ''

		for _ in range(choice(range(10, 50))):
			rndK += str(choice(Chars))

		return rndK

	def hash(self, password, tohash=False):
		if tohash: password = md5(password).hexdigest()

		password = password[16:] + password[:16]
		return password

	def loginEncrypt(self, password, rndK):
		encrypt = str(self.hash(password))
		encrypt += str(rndK)
		encrypt += "a1ebe00441f5aecb185d0ec178ca2305Y(02.>'H}t\":E1_root"

		encryption = self.hash(encrypt, True)

		return encryption