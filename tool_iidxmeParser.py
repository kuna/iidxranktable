# parses all users of SP10,11,12/DP10,11,12 data from iidx.me
# very much stress to server so don't execute this often.

import urllib
from bs4 import BeautifulSoup
import jsondata

# for DB
from flask import Flask
from db import db

def loadURL(url):
	res = urllib.urlopen(url)
	data = BeautifulSoup(res.read())
	return data

def getPageCount(soup):
	page = soup.find_all(class_="page")
	return int(page[len(page)-1].get_text())

def getAllUsers(pcnt):
	r = []

	def getUsers(soup, arr):
		names = soup.find_all(class_="djname")
		i = 0
		for name in names:
			if (i>0):
				arr.append(name)
			i+= 1

	for i in range(1, pcnt+1):
		print "parsing page %d" % i
		page = loadURL("http://iidx.me/?page=%d" % i)
		getUsers(page, r)

	return r

def parse(username, type, diff):
	def addUser(record):
		# only if user isn't exists
		user = db.Upload.query.filter_by(iidxid=record['userdata']['iidxid']).first()
		if not user:
			user = db.Player(iidxid=record['userdata']['iidxid'],\
				sppoint=, dppoint=,\
				spclass=, dpclass=)
			db.session.add(user)
			return user
		# TODO: if exists, update sppoint, spclass, etc.
		return user

	def addSong(record):
		# only if song isn't exists
		song = db.Song.query.filter_by(songid=record['data']['id']).first()
		if not song:
			song = db.Song(songid=,\
				songtype=, songtitle=,\
				songlevel=, songnotes=)
			db.session.add(song)
			return song
		return song

	def addRecord(player_, song_, record):
		# update in any case
		record = db.Song.query.filter_by(player=player_, song=song_).first()
		if not record:
			record = db.Record(player=, song=,\
				playtype=, playscore=,
				playrate=, playclear=,
				playmiss=)
			db.session.add(record)
			return record
		return record

	jsonurl = "http://json.iidx.me/%s/%s/level/%d" % (username, type, diff)
	record = jsondata.loadJSONurl(jsonurl)
	user = addUser(record)
	for music in record['musicdata']:
		song = addSong(music)
		record = addRecord(user, song, music)


# main code
print "--------------------------------"
print "* initalizing DB ..."
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_POOL_RECYCLE'] = 100
app.config['SQLALCHEMY_ECHO'] = False
db.init_app(app)
db.app = app
db.create_all()

####################################################

print "* loading iidx.me page ..."
iidxme = loadURL("http://iidx.me")

####################################################

print "* loading page count ..."
pcnt = getPageCount(iidxme)
print "-> %d" % pcnt

####################################################

print "* loading ALL USERs ..."
users = getAllUsers(pcnt)
print "-> %d users" % len(users)

####################################################

print "* loading User info & saving to DB ..."
# test code: 1~10
for i in range(0, 10):
	print "parsing %s,%s%d (%d/%d)" % (users[i], 'sp', 12, i, 10)
	parse(users[i], 'sp', 12)
db.session.commit()

####################################################

print "* calculating user levels ..."
# TODO. very much.

####################################################

print "Done!"