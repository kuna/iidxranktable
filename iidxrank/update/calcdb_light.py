#-*- coding: utf-8 -*-
#
# light version of difficulty calculation
# using MLE-like algorithm

import db
import math
from random import random as rand
import matplotlib.pyplot as plot		# only for debugee
from sqlalchemy import text

def norm(x, std):
	return 1/(math.sqrt(
		2*math.pi)*std)*math.exp(
		-(x-0)**2/(2*std**2))

def rnorm(std):
	return norm(rand()*10, std)

def randomTest(p):
	return p<=rand()

############################################################
# show us a little graph
def showSongStat():
	x = []
	y = []
	#for song in db.Song.query.all():
	for song in db.Song.query.filter(db.Song.songtype.startswith("SP")).all():
		x.append(song.songlevel)
		y.append(song.calclevel)
	plot.scatter(x, y, c='r')
	plot.show()

def showPlayerStat():
	x = []
	y = []
	for player in db.Player.query.all():
		x.append(player.spclass)
		y.append(player.splevel)
	plot.scatter(x, y, c='r')
	plot.show()


############################################################
def initDB():
	# need to set inital sp/dp level of player
	for player in db.Player.query.all():
		player.splevel = player.spclass
		player.dplevel = player.dpclass


# value: playrecord's player's dan
# weight: assist_clear: 1, easy_clear:2, groove_clear:1, hc=0.1, exh=0.05
# * multiply (miss count-10)
# level: (don't touch)
# using MLE-like algorithm
def calculate_song():
	songs = db.Song.query.all()
	i = 0

	for song in songs:
		print "%d/%d" % (i, len(songs))
		i += 1

		f_weight = 0
		f_value = 0
		for precord in song.playrecord:
			if (song.songtype[:2] == "SP"):
				val = precord.player.splevel
			else:
				val = precord.player.dplevel
			w = 0
			if (precord.playclear == 2):	# assist
				w = 1
			elif (precord.playclear == 3):	# easy
				w = 2
			elif (precord.playclear == 4):	# groove
				w = 1
			elif (precord.playclear == 5):	# hard
				w = 0.5
			elif (precord.playclear == 6):	# exhard
				w = 0.2
			w_miss = 1
			if (precord.playmiss):
				w_miss = precord.playmiss - 20
				if (w_miss < 0):
					w_miss = 0

			w *= w_miss
			f_weight += w
			f_value += val * w
		if (f_weight):
			song.calclevel = float(f_value) / f_weight
		else:
			song.calclevel = 0

# value: song's level
# weight: fullcombo: 20, exh:15, hard clear:10, easy clear:1,
# level weight: exp**2
def calculate_player():
	players = db.Player.query.all()
	i = 0

	for player in players:
		print "%d/%d" % (i, len(players))
		i += 1

		f_weight_sp = 0
		f_value_sp = 0
		f_weight_dp = 0
		f_value_dp = 0
		for precord in player.playrecord:
			val = precord.song.calclevel
			w = 3**precord.song.songlevel * 0.001
			if (precord.playclear == 3):	# easy
				w *= 1
			elif (precord.playclear == 4):	# groove
				w *= 2
			elif (precord.playclear == 5):	# hard
				w *= 3
			elif (precord.playclear == 6):	# exhard
				w *= 4
			elif (precord.playclear == 7):	# fc
				w *= 5
			if (precord.song.songtype[:2] == "SP"):
				f_weight_sp += w
				f_value_sp += val * w
			else:
				f_weight_dp += w
				f_value_dp += val * w
		if (f_weight_sp):
			player.splevel = float(f_value_sp) / f_weight_sp
		else:
			player.splevel = 0
		if (f_weight_dp):
			player.dplevel = float(f_value_dp) / f_weight_dp
		else:
			player.dplevel = 0



###########################################
#
# main func
#
###########################################

def main():
	print 'opening DB ...'
	global db_session
	db_session = db.init_db()

	print 'initalize...'
	initDB()

	print 'calculating song diff...'
	calculate_song()
	print 'calculating players ...'
	calculate_player()

	print 'song'
	showSongStat()
	print 'player'
	showPlayerStat()

	print 'commiting'
	db_session.commit()
	print 'finished. closing DB ...'
	db_session.remove()


if __name__=="__main__":
	main()