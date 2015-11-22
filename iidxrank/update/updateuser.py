#-*- coding: utf-8 -*-
#
# algorithm from: http://walkure.net/hakkyou/komakai.html#komakaihanashi
#
import db
import math
import parser_iidxme

# crolling user's information

#
# init_estimate: estimates user's default level
# - just estimate ... average level by clearing
#
def init_estimate():
	for player in db.Player.query.all():
		score = {'SP':0, 'DP':0}
		cnt = {'SP':0, 'DP':0}
		for playrecord in player.playrecord:
			songtype = playrecord.song.songtype[:-1]
			if (playrecord.playclear == 3):		# EASY CLEAR
				score[songtype] += playrecord.song.songlevel - 1
				cnt[songtype] += 1
			elif (playrecord.playclear == 4):	# GROOVE
				score[songtype] += playrecord.song.songlevel
				cnt[songtype] += 1
			elif (playrecord.playclear == 5):	# HARD
				score[songtype] += playrecord.song.songlevel + 1
				cnt[songtype] += 1
			elif (playrecord.playclear == 6):	# EX-HARD
				score[songtype] += playrecord.song.songlevel + 1
				cnt[songtype] += 1

		# make average and save it to DB
		if (cnt['SP']):
			player.splevel = score['SP'] / cnt['SP']
		else:
			player.splevel = None

		if (cnt['DP']):
			player.dplevel = score['DP'] / cnt['DP']
		else:
			player.dplevel = None


# iterate user level
def calculate_user():
	for player in db.Player.query.all():
		scoresum = {'SP':0, 'DP':0}
		weightsum = {'SP':0, 'DP':0}
		for playrecord in player.playrecord:
			songtype = playrecord.song.songtype[:-1]
			# big var. means not important => smaller weight
			if (playrecord.playclear == 3):		# EASY CLEAR
				scoresum[songtype] += (playrecord.song.calclevel - 1)\
					/ playrecord.song.calcweight
				weightsum[songtype] += 1/playrecord.song.calcweight
			elif (playrecord.playclear == 4):	# GROOVE
				scoresum[songtype] += (playrecord.song.calclevel)\
					/ playrecord.song.calcweight
				weightsum[songtype] += 1/playrecord.song.calcweight
			elif (playrecord.playclear == 5):	# HARD
				scoresum[songtype] += (playrecord.song.calclevel + 1)\
					/ playrecord.song.calcweight
				weightsum[songtype] += 1/playrecord.song.calcweight
			elif (playrecord.playclear == 6):	# EX-HARD
				scoresum[songtype] += (playrecord.song.calclevel + 1)\
					/ playrecord.song.calcweight
				weightsum[songtype] += 1/playrecord.song.calcweight

		# make average and save it to DB
		if (weightsum['SP']):
			player.splevel = float(scoresum['SP']) / weightsum['SP']
		else:
			player.splevel = None

		if (weightsum['DP']):
			player.dplevel = float(scoresum['DP']) / weightsum['DP']
		else:
			player.dplevel = None


# calculate song diff (from user)
# (should be called first)
# TODO calculate accurate step response
def calculate_song():
	# calculate average clear level ( -> b)
	for song in db.Song.query.all():
		score = 0
		cnt = 0

		# first calculate b (avg level)
		for playrecord in song.playrecord:
			if (song.songtype[:-1] == 'SP' and playrecord.player.splevel)
				score += playrecord.player.splevel
				cnt += 1
			elif (song.songtype[:-1] == 'DP' and playrecord.player.dplevel)
				score += playrecord.player.dplevel
				cnt += 1
		avglevel = float(score) / cnt
		song.calclevel = avglevel

		# then calculate a (weight)
		# -> related to variety (big var. means not important - smooth line)
		songweight = 0
		for playrecord in song.playrecord:
			if (song.playrecord > 2 and song.playrecord < 7):	# over assist under fullcombo
				playerlevel = 0
				if (song.songtype[:-1] == 'SP'):
					playerlevel = playrecord.player.splevel
				elif (song.songtype[:-1] == 'DP'):
					playerlevel = playrecord.player.dplevel
				if (playerlevel != None):
					songweight += math.pow(avglevel - playerlevel, 2)
		songweight = math.sqrt(float(songweight) / cnt)
		song.calcweight = songweight
 
#
# iterate - iterate each user's theta / and each song's a, b value
#
# calculate a, b, theta (sigmoid; step responsive model)
def iterate():
	for i in xrange(100):	# more count will get precise result
		# store previous user values to return error
		user_scores = []
		for player in db.Player.query.all():
			user_scores.append( {'SP': player.splevel, 'DP': player.dplevel} )

		calculate_user()
		calculate_song()

		# calculate error
		error_sum = 0
		for (player, score) in (db.Player.query.all(), user_scores):
			if (user_scores['SP']):
				error_sum += math.pow(player.splevel - user_scores['SP'], 2)
			if (user_scores['DP']):
				error_sum += math.pow(player.dplevel - user_scores['DP'], 2)

		print 'error: ' + math.sqrt(error_sum)

def stepresponse():
	# first initalize value
	init_estimate()
	# then start iteration
	iterate()

def update_user():
	add_count = 0
	for user in parser_iidx.parse_users():
		player_query = db.Player.query.filter_by(iidxid=user[2])
		if (player_query.count()):
			# edit nickname
			player = player_query.one()
			player.iidxnick = user[0]
			player.iidxmeid = user[1]
		else:
			# add new user
			player = db.Player(iidxid=user[2], 
					iidxnick=user[0],
					iidxmeid=user[1],
					sppoint=0,
					dppoint=0,
					spclass=0,
					dpclass=0,
					splevel=0,
					dplevel=0)
			db_session.add(player)
			add_count += 1
	print 'added %d items' % add_count

def update_user_from_data(player, user_info):
	add_count = 0
	# add clear data
	for playrecord in user_info['musicdata']:
		if (playrecord['clear'] > 2):	# only over assist clear
			song = db.Song.query.filter_by(songid=playrecord['data']['id'], songtype=playrecord['data']['diff'].upper())
			if (not song.count()):
				continue
			else:
				song = song.one()
			playrecord_query = db.PlayRecord.query.filter_by(player_id=player.id, song_id=song.id)
			if (playrecord_query.count()):
				# just update clear
				pr = playrecord_query.one()
				if (playrecord['score']):
					pr.playscore = playrecord['score']
				if (playrecord['miss']):
					pr.playmiss = playrecord['miss']
				pr.playclear = playrecord['clear']
			else:
				# add new one
				pr = db.PlayRecord(playscore=playrecord['score'],
					playclear=playrecord['clear'],
					playmiss=playrecord['miss'])
				db_session.add(pr)
				add_count += 1

	return add_count

def update_user_information():
	add_count = 0
	for player in db.Player.query.all():
		sppoint = 0
		dppoint = 0
		spclass = 0
		dpclass = 0
		# start from level 8
		for mode in ("sp", "dp"):
			for i in range(8, 13):
				user_info = parser_iidx.parse_user(player.iidxmeid, mode, i)
				sppoint = user_info['userdata']['sppoint']
				dppoint = user_info['userdata']['dppoint']
				spclass = user_info['userdata']['spclass']
				dpclass = user_info['userdata']['dpclass']
				add_count += update_user_from_data(player, user_info)
		player.sppoint = sppoint
		player.dppoint = dppoint
		player.spclass = spclass
		player.dpclass = dpclass

		print 'added %d playrecord' % add_count

def main():
	print 'opening DB ...'
	global db_session
	db_session = db.init_db()

	print 'crolling user list ...'
	update_user()

	print 'crolling user information ...'
	update_user_information()

	print 'iterating step-response-model'
	#stepresponse()

	# TODO: clean iidx member info for privacy?

	print 'finished. closing DB ...'
	db_session.remove()


if __name__=="__main__":
	main()