'''
Sound Studio handler
'''

#imports
from Tiles.Logs.Logger import Logger
from Engine.Packet import Packet
from Tiles.Database import Database, DictCursor
from time import time, sleep
from threading import Thread
from string import *
from random import *

class SStudio(object):

	def __init__(self):
		super(SStudio, self).__init__()
		self.broadcasting = list()
		self.endTimestamp = 0

	def init_sstudio(self):
		Logger().warn("Sound Studio is online!")
		self.broadCaster = Thread(target=self.Broadcaster)
		self.broadCaster.daemon = True
		self.loadedTracks = dict() # Track id : (penguin id, "track details/string")
		self.broadCaster.start()

		self.loadMusicTracks()

	def loadMusicTracks(self):
		Query = Database().prepare("SELECT `ID`, `MusicTracks`, `SharedTrack` FROM `penguins` WHERE 1")
		Query = Query.execute(DictCursor)
		details = Query.fetchallDict()
		Query = Database().prepare("SELECT * FROM `Musics` WHERE 1")
		tracks = Query.execute(DictCursor).fetchallDict()
		Penguins_by_track = dict()
		for detail in details:
			peng_id = str(int(detail['ID']))
			if detail['MusicTracks'] != None and detail['MusicTracks'] != "" and detail['MusicTracks'] != False:
				for TRACK in detail['MusicTracks'].split(";"):
					Penguins_by_track[str(TRACK)] = [peng_id, detail['SharedTrack'] if detail['SharedTrack'] != None else ""]

		for TrackDict in tracks:
			if str(int(TrackDict['Music ID'])) in Penguins_by_track:
				creator = Penguins_by_track[str(int(TrackDict['Music ID']))][0]
				sharedTrack = str(Penguins_by_track[str(int(TrackDict['Music ID']))][1])
				shared = "1" if str(int(TrackDict['Music ID'])) == sharedTrack else "0"
				liked = ''
				if TrackDict['Liked'] != None:
					liked = TrackDict['Liked']

				Hash  = TrackDict['Hash']
				name = TrackDict['Name']
				notes = TrackDict['Notes']
				likes = TrackDict['Likes']

				self.loadedTracks[str(int(TrackDict['Music ID']))] = [creator, [name, shared, likes, liked], notes, Hash]

	def swapBroadcasts(self):
		if len(self.broadcasting) <= 0:
			firstBroascast = self.broadcasting[0]
			self.broadcasting.remove(firstBroascast)
			self.broadcasting.append(firstBroascast)
		else:
			return

	def getPosition(self, id):
		id = str(id)
		position = "-1"

		for casting in self.broadcasting:
			if str(casting[0]) == id:
				position = str(self.broadcasting.index(casting) +1)
				break

		return position

	def updateBroadcasting(self, track, peng_name, peng_swid):
		track = str(track)
		details = self.loadedTracks[track]
		peng_id = str(details[0])

		broadcastArray = [peng_id, str(peng_name), str(peng_swid), track, str(details[1][2]), str(details[2])]
		broadcastingTracks = list(str(k[3]) for k in self.broadcasting)
		if track not in broadcastingTracks:
			self.broadcasting.append(broadcastArray)
			self.endTimestamp = 0


	def removeBroadcasting(self, track):
		broadcastingTracks = list(str(k[3]) for k in self.broadcasting)
		if str(track) in broadcastingTracks:
			index = -1
			for k in self.broadcasting:
				if str(k[3]) == str(track):
					index = self.broadcasting.index(k)
					break

			if index != -1:
				self.broadcasting.remove(self.broadcasting[int(index)])
				self.endTimestamp = 0

	def AppxMusicTime(self, notes, ctime):
		noteArray = str(notes).split(",")
		last_data = noteArray[-1].split("|")
		if last_data[0] == "FFFF":
			appx_time = int(last_data[1], 16) / 1000.0
			return ctime + (appx_time) #in secs!!

		return ctime # It's either no song, or incomplete song, or very short song.. etc,.

	def Broadcaster(self):
		while 1:
			currentTime = time()
			if len(self.broadcasting) > 0:
				if currentTime >= self.endTimestamp:
					musics = ",".join("|".join(k[:-2]) for k in self.broadcasting)
					count = str(len(self.broadcasting))				

					for socket, penguin in self._penguins.iteritems():
						playerPosition = self.getPosition(penguin.id)
						penguin.sendWorldPacket("broadcastingmusictracks", count, playerPosition, musics)
						self.swapBroadcasts()

					self.endTimestamp = self.AppxMusicTime(self.broadcasting[0][-1], currentTime)

				else:
					sleep(1)
					continue
			else:
				self.endTimestamp = 0
				for socket, penguin in self._penguins.iteritems():
					penguin.sendWorldPacket("broadcastingmusictracks", "0", "-1", "")
				sleep(25)
				continue

	def FetchMyMusicTracks(self, socket):
		penguin = self._penguins[socket]

		penguinMusics = penguin.database.getColumnById(penguin.id, "MusicTracks")
		userTrackString = list()
		userTrackCount = 0

		if penguinMusics != "" and penguinMusics != False and penguinMusics != None:
			penguinSavedTracks = penguinMusics.split(";")

			for Track in penguinSavedTracks:
				if str(Track) in self.loadedTracks: #else unavailable track..
					if str(self.loadedTracks[str(Track)][0]) == str(penguin.id):
						name, shared, likes, liked = self.loadedTracks[str(Track)][1]
						userTrackString += ["|".join((str(Track), str(name), str(shared), str(likes)))] # Music ID, Music Name, Music shared (1/0), Music Likes

		userTrackCount = str(len(userTrackString))

		penguinMusicString = ",".join(userTrackString)
		penguin.sendWorldPacket("getmymusictracks", userTrackCount, penguinMusicString)

	def SaveMyMusic(self, socket):
		penguin = self._penguins[socket]

		music_name = Packet.Data[2]
		music_notes = Packet.Data[3]
		music_hash = Packet.Data[4]

		music_id = penguin.database.executeMe("INSERT INTO `Musics` (`Name`, `Notes`, `Hash`, `Likes`, `Liked`) VALUES ('{0}', '{1}', '{2}', '0', '')".format(
			music_name, music_notes, music_hash)).lastrowid

		penguin.database.executeMe("UPDATE `penguins` SET `MusicTracks` = TRIM(BOTH ';' FROM CONCAT(MusicTracks, ';{0}'))".format(music_id))
		self.loadedTracks[str(music_id)] = [str(penguin.id), [str(music_name), '0', '0', []], music_notes, music_hash]

		penguin.send("savemymusictrack", music_id)

	def GetMySharedTracks(self, socket):
		penguin = self._penguins[socket]

		shared_track = str(penguin.database.getColumnById(penguin.id, "SharedTrack"))
		if shared_track != "" and shared_track != False and shared_track != None and shared_track in self.loadedTracks:
			track_details = self.loadedTracks[shared_track][1]
			name, shared, likes, liked = track_details

			sharedTrackString = ",".join((shared_track, str(name), str(shared), str(likes)))

			penguin.sendWorldPacket("getsharedmusictracks", "1", sharedTrackString)
		else:
			penguin.sendWorldPacket("getsharedmusictracks", "0", "")

	def DeleteMyMusic(self, socket):
		penguin = self._penguins[socket]

		Track_id = str(Packet.Data[2])
		if Track_id in self.loadedTracks:
			details = self.loadedTracks[Track_id]
			if str(details[0]) == str(penguin.id):
				name, shared, likes, liked = details[1]
				if shared == "1":
					penguin.database.updateColumnById(penguin.id, "SharedTrack", "")

				self.removeBroadcasting(Track_id)
				penguin.database.executeMe("DELETE FROM `Musics` WHERE `Music ID`='{0}'".format(Track_id))
				penguin.database.executeMe("UPDATE `penguins` SET `MusicTracks` = TRIM(BOTH ';' FROM REPLACE(MusicTracks, '{0}', '')) WHERE `ID` = '{1}'".format(
					Track_id, penguin.id))
				del self.loadedTracks[Track_id]

				penguin.sendWorldPacket("deletetrack", "1")

	def LoadMusicByTrack(self, socket):
		penguin = self._penguins[socket]

		user = str(Packet.Data[2])
		tracks = Packet.Data[3:]

		loadedTracks = list()

		for track in tracks:
			if track in self.loadedTracks:
				details = self.loadedTracks[track]
				if str(details[0]) == user:
					name, shared, likes, liked = details[1]
					notes = details[2]
					Hash = details[3]

					loadedTracks.append("%".join((str(track), str(name), str(shared), str(notes), str(Hash), str(liked))))

		loadedTrackString = "%-1%".join(loadedTracks)
		penguin.sendWorldPacket("loadmusictrack", loadedTrackString)

	def ShareTrack(self, socket):
		penguin = self._penguins[socket]

		track = str(Packet.Data[2])
		share = str(Packet.Data[3]) == "1"

		if track in self.loadedTracks:
			if str(self.loadedTracks[track][0]) == str(penguin.id):
				if share:
					sharing = str(penguin.database.getColumnById(penguin.id, "SharedTrack"))
					if sharing != "" and sharing != False and sharing != None:
						self.removeBroadcasting(sharing)
					
					self.updateBroadcasting(track, penguin.username, penguin.swid)
					
					penguin.database.updateColumnById(penguin.id, "SharedTrack", track)
					penguin.sendWorldPacket("sharemymusictrack", "1")

				else:
					sharing = str(penguin.database.getColumnById(penguin.id, "SharedTrack"))
					if sharing != "" and sharing != False and sharing != None:
						self.removeBroadcasting(sharing)

					if sharing != track:
						self.removeBroadcasting(track)

					penguin.database.updateColumnById(penguin.id, "SharedTrack", "")
					penguin.sendWorldPacket("sharemymusictrack", "1", "|".join([track, "0"]))					

	def BroadcastMusic(self, socket):
		penguin = self._penguins[socket]

		musics = ",".join("|".join(k) for k in self.broadcasting)
		count = str(len(self.broadcasting))				

		playerPosition = self.getPosition(penguin.id)
		penguin.sendWorldPacket("broadcastingmusictracks", count, playerPosition, musics)

	def RefreshMusicLikes(self, socket):
		penguin = self._penguins[socket]
		peng_musics = penguin.database.getColumnById(penguin.id, "MusicTracks")
		musics = peng_musics.split(";") if peng_musics !=  None and peng_musics != False and peng_musics != "" else list()
		try: musics.remove("")
		except: pass

		for track in musics:
			if str(track) in self.loadedTracks:
				details = self.loadedTracks[str(track)]
				if str(details[0]) == str(penguin.id):
					name, shared, likes, liked = details[1]
					penguin.sendWorldPacket("getlikecountfortrack", str(penguin.id), str(track), str(likes))

	def LikePlayerTrack(self, socket):
		penguin = self._penguins[socket]

		peng_id = str(Packet.Data[2])
		track = str(Packet.Data[3])

		if track in self.loadedTracks:
			details = self.loadedTracks[track]
			if str(details[0]) == str(peng_id):
				name, shared, likes, liked = details[1]
				pengs_likes = {
					str(k.split(":")[0]) : int(round(k.split(":")[1])) for k in liked.split(",") if liked != ""
				}
				currentTime = time()

				if str(penguin.id) in pengs_likes:
					liked_timestamp = int(pengs_likes[str(penguin.id)])
					if currentTime - liked_timestamp > 0:
						# He can like it ;)
						self.loadedTracks[track][1][2] = str(int(likes)+1)
						pengs_likes[str(penguin.id)] = time() + (24 * 60*60)
						likeStrings = [str(k)+":"+str(pengs_likes[k]) for k in pengs_likes]
						likedString = ",".join(likeStrings)
						self.loadedTracks[track][1][3] = likedString

						penguin.database.executeMe("UPDATE `Musics` SET `Likes` = Likes + 1 WHERE `Music ID`='{0}'".format(track))
						penguin.database.executeMe("UPDATE `Musics` SET `Liked`='{0}' WHERE `Music ID`='{1}'".format(
							likedString, track))

				else:
					# He can like it ;)
					pengs_likes[str(penguin.id)] = time() + (24 * 60*60)
					self.loadedTracks[track][1][2] = str(int(likes)+1)
					pengs_likes[str(penguin.id)] = time() + (24 * 60*60)
					likeStrings = [str(k)+":"+str(pengs_likes[k]) for k in pengs_likes]
					likedString = ",".join(likeStrings)
					self.loadedTracks[track][1][3] = likedString

					penguin.database.executeMe("UPDATE `Musics` SET `Likes` = Likes + 1 WHERE `Music ID`='{0}'".format(track))
					penguin.database.executeMe("UPDATE `Musics` SET `Liked`='{0}' WHERE `Music ID`='{1}'".format(
						likedString, track))

			penguin.sendWorldPacket("liketrack", str(peng_id), str(track), str(self.loadedTracks[track][1][2]))

	def CanLikeMyTrack(self, socket):
		penguin = self._penguins[socket]

		peng_id = Packet.Data[2]
		track = Packet.Data[3]

		if track in self.loadedTracks:
			details = self.loadedTracks[track]
			if str(details[0]) == str(peng_id):
				name, shared, likes, liked = details[1]

				pengs_likes = {
					str(k.split(":")[0]) : int(k.split(":")[1]) for k in liked.split(",") if liked != ""
				}
				currentTime = time()

				if str(penguin.id) in pengs_likes:
					liked_timestamp = int(pengs_likes[str(penguin.id)])
					if currentTime - liked_timestamp > 0:
						penguin.sendWorldPacket("canliketrack", str(track), "1")
					else:
						penguin.sendWorldPacket("canliketrack", str(track), "0")

				else:
					penguin.sendWorldPacket("canliketrack", str(track), "1")

