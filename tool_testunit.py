# -*- coding: utf-8 -*-
import song
import jsondata
import copy

def test(json):
	option = jsondata.loadJSONfile(json)
	print "----------------------------------------------------"
	print "--- %s " % (option['title'])
	print "----------------------------------------------------"
	songdata = song.getCSVdata(option["datafile"])
	userdata = jsondata.loadJSONfile(option["jsonfile"])
	orig_userdata = copy.deepcopy(userdata)
	duplicatecheck = {}
	for songs in songdata:
		for song_ in songs["songs"]:
			# ALL option: no need to continue
			if (song_['option'] == 'ALL'):
				userdata["musicdata"] = []
				break;

			if (not song.isexists(userdata["musicdata"], song_, True)):
				print "unmatched(redundant) song exists in RANKFILE - %s/%s (%s)" % (song_["id"], song_["option"], songs["category"])

			code = str(song_["id"]) + str(song_["option"])
			if (code in duplicatecheck):
				d = song.isexists(orig_userdata["musicdata"], song_)
				print "song seems like duplicated in RANKFILE - %s/%s (%s) (title: %s)" % \
				(song_["id"], song_["option"], songs["category"], d['data']['title'])

			duplicatecheck[code] = 0


	if (len(userdata["musicdata"]) > 0):
		print "REDUNT MUSICDATA FOUND! DATABASE UPDATE NECESSARY"
		for d in userdata["musicdata"]:
			print d['data']['id']
			#print u"%s (%s)" % (d['data']['title'].encode('utf8', 'ignore').decode('utf8', 'ignore'), d['data']['id'])



print "checking any invalid data exists..."

# TODO: automatically find all *.json files
test("./data/sp.10.json")
test("./data/sp.11.json")
test("./data/sp.12.json")
test("./data/sp.12.7.json")
test("./data/dp.10.json")
test("./data/dp.11.json")
test("./data/dp.12.json")

