#-*- coding: utf-8 -*-
import io, json
import jsondata
import urllib
from bs4 import BeautifulSoup

#
# parse_users: return user lists
#
def parse_users():
	def parse_users_page(num, arr):
		def getUsers(soup, arr):
			names = soup.find_all(class_="djname")
			i = 0
			for name in names:
				if (i>0):
					arr.append(name.get_text())
				i+= 1

		data = urllib.urlopen("http://iidx.me/?page=%d" % num)
		soup = BeautifulSoup(data.read())
		getUsers(soup, arr)


	def getPageCount():
		data = urllib.urlopen("http://iidx.me")
		soup = BeautifulSoup(data.read())
		page = soup.find_all(class_="page")
		return int(page[len(page)-1].get_text())
	
	pcnt = getPageCount()
	r = []
	for i in range(1, pcnt+1):
		print 'parsing page %d ...' % i
		parse_users_page(i, r)
	return r

#
# parse_user: return user info
# (djname, iidxid, ...)
#
def parse_user(username):
	parsedata = jsondata.loadJSONurl("http://json.iidx.me/delmitz/sp/level/" + str(level))

	return parsedata['userdata']

#
# parse_songs: return songs in level
# (title, level, notes, version, diff, id ...)
#
def parse_songs(level):
	parsedata = jsondata.loadJSONurl("http://json.iidx.me/delmitz/sp/level/" + str(level))

	# remove scores
	ret = []
	#del parsedata['userdata']
	#del parsedata['status']
	for music in parsedata['musicdata']:
		#del music['clear']
		#del music['score']
		#del music['miss']
		ret.append(music['data'])

	return ret

#
# parse_clearinfo: get user's all clear datas
# ()
#
def parse_clearinfo(username):
	pass

print parse_users()