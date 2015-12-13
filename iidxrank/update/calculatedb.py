#-*- coding: utf-8 -*-
#
# using MCMC algorithm

import db
import math
from random import random as rand
import random
from sqlalchemy import text
import log

# basic initalization
db_session = db.get_session()
diffs = ['easy', 'normal', 'hd', 'exh']
diffs_num = {'easy':3, 'normal':4, 'hd':5, 'exh':6}

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
def model_user(a, b, x):
	return 1/(1+math.exp(-a*(x-b)))
def model_song(a, b, x):
	return 1/(1+math.exp(a*(x-b)))

# make score per clear status
# (used for player)
def clearScore(playclear, type=None):
	if (type == None):
		if (playclear == 1):
			return 0
		elif (playclear == 2):
			return 0
		elif (playclear == 3):
			return 0.3
		elif (playclear == 4):
			return 0.4
		elif (playclear == 5):
			return 0.7
		elif (playclear == 6):
			return 0.9
		elif (playclear == 7):
			return 1

	def getScoreValue(clear_goal):
		if (playclear < clear_goal):
			return 0
		else:
			return 1
	if (type in diffs_num):
		return getScoreValue(diffs_num[type])
	else:
		raise Exception("unsupported type of difficulty")

# reject if player has no playrecord / no fail / only fullcombo
def checkValidPlayer(player):
	if (len(player.playrecord) == 0):
		return False
	return True

############################################################
# update every user/song level
# using MCMC algorithm
def iterate_song(_range=(-0.5, 0.5), iterate_time=5, diff="hd"):
	calclevel_diff = "calclevel_" + diff
	calcweight_diff = "calcweight_" + diff

	# get clearrate of users whose level is enough
	def getScore(song, level, weight):
		cul = 0
		for precord in song.playrecord:
			if (precord.playclear == 0):	# ignore noclear
				continue
			v = clearScore(precord.playclear, diff)
			player_level = 0
			if (song.songtype[:2] == "SP"):
				player_level = precord.player.splevel
			else:
				player_level = precord.player.dplevel
			# ignore too much low or high score
			if (player_level >2 or player_level < 18):
				continue
			# get models' clear estimation of suggested 'level'
			cul += (v - model_song(weight, player_level, level))**2	# model is inversed in song!
		return cul

	i = 0
	songs = db_session.query(db.Song).all()
	error_sum = 0
	for song in songs:
		if (i%10==0):
			log.Print("%d/%d" % (i, len(songs)))
		i+=1

		# if song has no playrecord
		# then ignore
		if (len(song.playrecord) == 0):
			setattr(song, calclevel_diff, 0)

		# smaller score is better
		# random walk for 5 times (for level)
		cur_lv = getattr(song, calclevel_diff)
		cur_weight = getattr(song, calcweight_diff)
		if (cur_lv>20):
			cur_lv = 20
			cur_weight = 10
		elif (cur_lv<0):	# too small value
			cur_lv = 0
			cur_weight = 10
		if (cur_weight > 20):
			cur_weight = 20
		elif (cur_weight < 1):
			cur_weight = 1
		lvls = [cur_lv,]
		scores = [getScore(song, lvls[0], cur_weight),]
		for t in range(iterate_time):
			new_level = cur_lv + random.uniform(_range[0], _range[1])
			lvls.append(new_level)
			scores.append(getScore(song, new_level, cur_weight))
		setattr(song, calclevel_diff, lvls[scores.index(min(scores))])

		# random walk for 5 times (for weight)
		cur_lv = getattr(song, calclevel_diff)
		lvls = [cur_weight,]
		scores = [getScore(song, cur_lv, lvls[0]),]
		for t in range(iterate_time):
			new_weight = cur_weight + random.uniform(_range[0], _range[1])*0.1*cur_weight
			lvls.append(new_weight)
			scores.append(getScore(song, cur_lv, new_weight))
		setattr(song, calcweight_diff, lvls[scores.index(min(scores))])

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
			for diff in ["easy", "hd", "exh"]:
				calclevel = getattr(precord.song, 'calclevel_'+diff)
				if (calclevel < 2 or calclevel > 18):	# too low level or too high level is wrong calculated: ignore
					continue
				v = clearScore(precord.playclear, diff)			# real value (model: expected)
				cul += (v - model_user(5, calclevel, level))**2	# weight is 5, maybe
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
	players = db_session.query(db.Player).all()
	error_sum = 0
	for player in players:
		if (i%10==0):
			log.Print("%d/%d" % (i, len(players)))
		i+=1

		error_sum += calculate_player(player, _range, iterate_time)
	return error_sum

######################################
# initalize DB with zero value
def initDB_Zero():
	log.Print('initalizing to Zero ...')
	for song in db_session.query(db.Song).all():
		for d in diffs:
			setattr(song, "calclevel_"+d, 0)
			setattr(song, "calcweight_"+d, 0)

######################################
# initalize DB 
def initDB():
	# set inital values for calculation (song)
	log.Print('initalize ...')
	for song in db_session.query(db.Song).all():
		pclear = []
		for precord in song.playrecord:
			pclear.append(precord.playclear)
		# if no score data, then songlevel is 0 (unknown)
		if (len(pclear) == 0):
			for diff in diffs:
				setattr(song, 'calclevel_'+diff, 0)
				setattr(song, 'calcweight_'+diff, 10)
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
		for diff in diffs:
			setattr(song, 'calclevel_'+diff, song.songlevel + float(i)/len(pclear) + 1-pclear_score_avg)
			setattr(song, 'calcweight_'+diff, 10)	# default is 10

	# set inital values for calculation (player)
	# do MCMC like method to estimate player (wide range)
	for player in db_session.query(db.Player).all():
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

def calc_song_rough(d=None):
	log.Print("songlevel_stabilizing_rough")
	for i in range(1):
		log.Print("iteration %d" % i)
		if (d == None):
			d = diffs
		for diff in d:
			print diff
			iterate_song((-4, 4), 10, diff)

def calc_player_stable():
	log.Print("playerlevel_stabilizing")
	for i in range(30):
		log.Print("iteration %d" % i)
		iterate_player((-0.5, 0.5), 2)

def calc_song_stable(d=None):
	log.Print("songlevel_stabilizing")
	for i in range(30):
		log.Print("iteration %d" % i)
		if (d == None):
			d = diffs
		for diff in d:
			print diff
			iterate_song((-0.5, 0.5), 2, diff)

def calc_MCMC():
	for i in range(20):
		log.Print("iteration %d" % i)
		for diff in diffs:
			iterate_song((-0.5, 0.5), 3, diff)
		iterate_player((-0.5, 0.5), 3)
		if (True):
			log.Print('song')
			#showSongStat("SP", True, "songstatSP%d.png"%i)
			#showSongStat("DP", True, "songstatDP%d.png"%i)
			log.Print('player')
			showPlayerStat(True, "playerstat%d.png"%i)
		if ((i+1)%10 == 0):
			db_session.commit()

def main():
	# you may comment this initing process if it's bad
	#initDB()

	# make player stable
	#calc_player_stable()

	# make song stable
	#calc_song_rough()
	#calc_song_stable()

	# full iteration
	calc_MCMC()

	log.Print('finished. closing DB ...')
	db.commit()
	db.remove()


if __name__=="__main__":
	main()

