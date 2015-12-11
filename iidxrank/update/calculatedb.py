#-*- coding: utf-8 -*-
#
# using MCMC algorithm

import db
import math
from random import random as rand
import random
from sqlalchemy import text
import log

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
def showSongStat(type="SP", onlysave=True, fname="songstat.png"):
	import matplotlib.pyplot as plot		# only for debugee
	if (len(type) != 2):
		raise Exception("invalid song type")

	x = []
	y = []
	for song in db.Song.query.all():
		if (song.songtype[:2] == "SP"):
			x.append(song.songlevel)
			y.append(song.calclevel)
	plot.scatter(x, y, c='r')
	if (onlysave):
		plot.savefig(fname)
	else:
		plot.show()
	plot.clf()

def showPlayerStat(onlysave=True, fname="playerstat.png"):
	import matplotlib.pyplot as plot		# only for debugee
	x = []
	y = []
	for player in db.Player.query.all():
		x.append(player.spclass)
		y.append(player.splevel)
	plot.scatter(x, y, c='r')
	if (onlysave):
		plot.savefig(fname)
	else:
		plot.show()
	plot.clf()

# using model (from walkure)
def model(a, b, x):
	return 1/(1+math.exp(a*(x-b)))

# make score per clear status
def clearScore(playclear):
	if (playclear <= 2):	# under assist: score failed
		return 0
	elif (playclear == 3):	# easy clear
		return 0.1
	elif (playclear == 4):	# groove clear
		return 0.2
	elif (playclear == 5):	# hard
		return 0.9
	elif (playclear == 6):	# exh
		return 0.95
	elif (playclear == 7):	# fc
		return 1

############################################################
# update every user/song level
# using MCMC algorithm
def iterate_song(_range=(-0.5, 0.5), iterate_time=5):
	# get clearrate of users whose level is enough
	def getScore(song, level, weight):
		cul = 0
		for precord in song.playrecord:
			if (precord.playclear == 0):	# ignore noclear
				continue
			v = clearScore(precord.playclear)
			player_level = 0
			if (song.songtype[:2] == "SP"):
				player_level = precord.player.splevel
			else:
				player_level = precord.player.dplevel
			cul += abs(v - model(-weight, level, player_level))	# model is inversed in song!
		return cul

	i = 0
	songs = db.Song.query.all()
	error_sum = 0
	for song in songs:
		if (i%10==0):
			log.Print("%d/%d" % (i, len(songs)))
		i+=1

		# smaller score is better
		# random walk for 5 times (for level)
		lvls = [song.calclevel,]
		scores = [getScore(song, lvls[0], song.calcweight),]
		for t in range(iterate_time):
			new_level = song.calclevel + random.uniform(_range[0], _range[1])
			lvls.append(new_level)
			scores.append(getScore(song, new_level, song.calcweight))
		song.calclevel = lvls[scores.index(min(scores))]

		# random walk for 5 times (for weight)
		lvls = [song.calcweight,]
		scores = [getScore(song, song.calclevel, lvls[0]),]
		for t in range(iterate_time):
			new_weight = song.calcweight + random.uniform(_range[0], _range[1])*0.1*song.calcweight
			if (new_weight > 20):
				new_weight = 20
			elif (new_weight < 0.5):
				new_weight = 0.5
			lvls.append(new_weight)
			scores.append(getScore(song, song.calclevel, new_weight))
		song.calcweight = lvls[scores.index(min(scores))]
		error_sum += min(scores)
	return error_sum

def calculate_player(player, _range=(-0.5, 0.5), iterate_time=20):
	def getScore(player, level, type):
		cul = 0
		for precord in player.playrecord:
			if (precord.song.songtype[:2] != type):	# check song type
				continue
			if (precord.playclear == 0):	# ignore noclear
				continue

			# get current clear state
			v = clearScore(precord.playclear)
			cul += abs(v - model(5, level, precord.song.calclevel))	# weight is 5, maybe
		return cul

	# random walk for 10 times
	lvls = [player.splevel,]
	scores = [getScore(player, lvls[0], "SP"),]
	for t in range(iterate_time):
		new_level = player.splevel + random.uniform(_range[0], _range[1])
		lvls.append(new_level)
		scores.append(getScore(player, new_level, "SP"))
	player.splevel = lvls[scores.index(min(scores))]

	# random walk for 10 times
	lvls = [player.dplevel,]
	scores = [getScore(player, lvls[0], "DP"),]
	for t in range(iterate_time):
		new_level = player.dplevel + random.uniform(_range[0], _range[1])
		lvls.append(new_level)
		scores.append(getScore(player, new_level, "DP"))
	player.dplevel = lvls[scores.index(min(scores))]
	return min(scores)

def calculate_player_by_name(iidxmeid, _range=(-0.5, 0.5), iterate_time=15):
	player = db.Player.query.filter_by(iidxmeid=iidxmeid).one()
	# in case of this player hadn't played any(or big difference), initalize it
	log.Print('initalize player level ...')
	calculate_player(player, (0, 12), 10)
	log.Print('detailing player level ...')
	return calculate_player(player, _range, iterate_time)

def iterate_player(_range=(-0.5, 0.5), iterate_time=5):
	i = 0
	players = db.Player.query.all()
	error_sum = 0
	for player in players:
		if (i%10==0):
			log.Print("%d/%d" % (i, len(players)))
		i+=1

		error_sum += calculate_player(player, _range, iterate_time)
	return error_sum


def initDB():
	# set inital values for calculation (song)
	log.Print('initalize ...')
	for song in db.Song.query.all():
		pclear = []
		for precord in song.playrecord:
			pclear.append(precord.playclear)
		# if no score data, then songlevel is 0 (unknown)
		if (len(pclear) == 0):
			song.calclevel = 0
			song.calcweight = 10
			continue

		# 1. check average clear score
		# high average, low difficulty
		pclear_score_avg = sum([clearScore(_c) for _c in pclear]) / float(len(pclear))

		# 2. check ratio of hard clear
		# high ratio of easy clear, high difficulty
		pclear.sort()
		i = 0
		for _c in pclear:
			if _c >= 5:	# greedy method to check diff (hard difficulty)
				break
			i += 1
		# gather all the information
		song.calclevel = song.songlevel + float(i)/len(pclear) + 1-pclear_score_avg
		song.calcweight = 10.0		# default is 10

	# set inital values for calculation (player)
	# do MCMC like method to estimate player (wide range)
	for player in db.Player.query.all():
		player.splevel = 0	# init
		player.dplevel = 0	# init
	iterate_player((0, 13), 100)

	# show us a little graph
	#showSongStat()
	#showPlayerStat()

###########################################
#
# main func
#
###########################################

def calc_player_rough():
	log.Print("playerlevel_stabilizing_rough")
	for i in range(1):
		log.Print("iteration %d" % i)
		iterate_player((-14, 14), 40)

def calc_song_rough():
	log.Print("songlevel_stabilizing_rough")
	for i in range(1):
		log.Print("iteration %d" % i)
		iterate_song((-14, 14), 40)

def calc_player_stable():
	log.Print("playerlevel_stabilizing")
	for i in range(50):
		log.Print("iteration %d" % i)
		iterate_player((-0.2, 0.2), 2)

def calc_song_stable():
	log.Print("songlevel_stabilizing")
	for i in range(50):
		log.Print("iteration %d" % i)
		iterate_song((-0.2, 0.2), 2)

def calc_MCMC():
	for i in range(20):
		log.Print("iteration %d" % i)
		iterate_song((-0.2, 0.2), 3)
		iterate_player((-0.2, 0.2), 3)
		if (True):
			log.Print('song')
			#showSongStat("SP", True, "songstatSP%d.png"%i)
			#showSongStat("DP", True, "songstatDP%d.png"%i)
			log.Print('player')
			showPlayerStat(True, "playerstat%d.png"%i)
		if ((i+1)%10 == 0):
			db_session.commit()

def main():
	log.Print('opening DB ...')
	global db_session
	db_session = db.init_db()

	# you may comment this initing process if it's bad
	#initDB()

	# make player stable
	#calc_player_stable()

	# make song stable
	#calc_song_stable()

	# full iteration
	calc_MCMC()

	log.Print('finished. closing DB ...')
	db_session.commit()
	db_session.remove()


if __name__=="__main__":
	main()

