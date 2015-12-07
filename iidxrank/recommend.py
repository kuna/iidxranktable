import models
from update import calculatedb		# to use model
import iidx

# a simple common func
def avg(ar):
	if (len(ar) == 0):	# div by 0 error
		return 0
	return sum(ar) / float(len(ar))

def safeInt(v):
	if (v == None):
		return 0
	try:
		return int(v)
	except:
		return 0

###########################################################

def getSimilarUsers(player, playtype="SP"):
	if (playtype=="SP"):
		return models.Player.objects.filter(splevel__gt=player.splevel-0.3, splevel__lt=player.splevel+0.3).all()
	elif (playtype=="DP"):
		return models.Player.objects.filter(dplevel__gt=player.dplevel-0.3, dplevel__lt=player.dplevel+0.3).all()
	else:
		raise Exception("improper playtype - %s" % playtype)

def getScoreRate(precord):
	if (precord.song.songnotes == None or precord.song.songnotes == 0):
		return 0
	else:
		if (precord.playscore == None):
			return 0
		else:
			return precord.playscore / float(precord.song.songnotes*2)

def getPlayRecords(users, song):
	return filter(lambda pr: pr.player in users,
		models.PlayRecord.objects.filter(song=song).all())

def getAverageScore(precords):
	return avg(filter(lambda x: x!=None, [pr.playscore for pr in precords]))

def getAverageClear(precords):
	return avg([pr.playclear for pr in precords])

def getClearProbability(precords, clear):
	total = 0
	num = 0
	for precord in precords:
		if (precord.playclear == None):
			continue
		if (precord.playclear > 0):
			total += 1
		if (precord.playclear >= clear):
			num += 1
	return float(num) / total

#################################################
# this method is very slow
# so we're goint go use another fast method
def findRecommend(player, playtype="SP"):
	recommend_song = []

	# find similar users
	similar_users = getSimilarUsers(player, playtype)

	# search this player's played records
	for precord in player.playrecord_set.all():
		# check song type
		if (precord.song.songtype[:2] != playtype):
			continue
		# TODO remove this part - TEST: only 10 level
		if (precord.song.songlevel != 10):
			continue

		recommend_info = {
			'songtitle': precord.song.songtitle,
			'songlevel': precord.song.songlevel,
			'curscore': safeInt(precord.playscore),
			'rate': getScoreRate(precord),
			'score': 0,		# how much score can be updated (grammar?)
			'clear': 0,		# how much percent can we update clear lamp
			'clears': [],
		}
		precords_similar = getPlayRecords(similar_users, precord.song)
		# we can't recommend if there's no similar users
		if (len(precords_similar) == 0):
			continue

		avg_score = getAverageScore(precords_similar)
		avg_clear = getAverageClear(precords_similar)
		# check is playscore under avg
		if (precord.playscore != None and precord.playscore < avg_score):
			recommend_info['score'] = avg_score - precord.playscore
		# check is clear status under avg
		if (precord.playclear != None and precord.playclear < avg_clear):
			# fail (or assist)
			recommend_info['clears'].append(round(getClearProbability(precords_similar, 2)*100))
			# easy
			recommend_info['clears'].append(round(getClearProbability(precords_similar, 3)*100))
			# clear
			recommend_info['clears'].append(round(getClearProbability(precords_similar, 4)*100))
			# hard
			recommend_info['clears'].append(round(getClearProbability(precords_similar, 5)*100))
			# exh
			recommend_info['clears'].append(round(getClearProbability(precords_similar, 6)*100))
			# fc
			recommend_info['clears'].append(round(getClearProbability(precords_similar, 7)*100))
			# current clear state
			recommend_info['clear'] = round(getClearProbability(precords_similar, precord.playclear+1)*100)

		# is it recommendable?
		if (recommend_info['score'] > 0 or recommend_info['clear'] > 0):
			recommend_song.append(recommend_info)

	return recommend_song

###################################################
# fast calculation /w p(theta) (algorithm from walkure)
#
def findRecommend_fast(player, playtype="SP", level=-1):
	recommend_song = []

	mylevel = player.splevel
	if (playtype == "DP"):
		mylevel = player.dplevel

	# prefetch playrecords (performance important!)
	precords = player.playrecord_set.select_related('song').all()
	print 'fetch okay (%d)' % len(precords)

	# search this player's played records
	for song in models.Song.objects.filter(songtype__istartswith=playtype).all():
		# if level is not fit then ignore
		if (level != -1 and song.songlevel != int(level)):
			continue
		# ignore not-calculated song
		if (song.calclevel == 0):
			continue

		# find play record
		# IMPORTANT filter query is VERY SLOW!
		# (it seems like it don't use cached records...)
		try:
			precord = precords.get(song=song)
		except:
			precord = None

		if (precord == None):
			playscore = 0
			rate = 0
			current_clear = 0
		else:
			playscore = safeInt(precord.playscore)
			rate = getScoreRate(precord)
			current_clear = precord.playclear

		recommend_info = {
			'songtitle': song.songtitle,
			'songtype': song.songtype,
			'songlevel': song.songlevel,
			'curscore': playscore,
			'rate': rate,
			'score': 0,		# how much score can be updated (grammar?)
			'clear': 0,		# how much percent can we update clear lamp
			'clears': [],
			'target': '',
		}

		# get clear probability
		###########################################
		# this is not accurate! (try to be accurate)
		###########################################
		my_clear_prob = [
			100,	# noplay
			100,	# fail
			100,	# assist
			round(calculatedb.model(-song.calcweight, song.calclevel-0.6, mylevel)*100),	# easy 3
			round(calculatedb.model(-song.calcweight, song.calclevel, mylevel)*100),	# groove 4
			round(calculatedb.model(-song.calcweight, song.calclevel+0.3, mylevel)*100),		# hard 5
			round(calculatedb.model(-song.calcweight, song.calclevel+1.0, mylevel)*100),	# exh
			round(calculatedb.model(-song.calcweight, song.calclevel+2.3, mylevel)*100),	# fc
		]
		target_clear = 0
		for i in range(8):
			if (my_clear_prob[i] > 50):
				target_clear = i
			else:
				break
		# over easy clear & better than current
		if (target_clear >= 3 and current_clear < target_clear):
			recommend_info['clear'] = my_clear_prob[target_clear]
			recommend_info['clears'] = my_clear_prob
			recommend_info['target'] = iidx.getclearstring_simple(target_clear)

		# is it recommendable?
		if (recommend_info['score'] > 0 or recommend_info['clear'] > 50):
			recommend_song.append(recommend_info)

	return recommend_song