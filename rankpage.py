from flask import Flask, render_template, abort
import iidx
import jsondata
import song
import db

def render_score(player, score, option_):
	name = ""
	spdan = ""
	dpdan = ""
	if (player):
		name = player['userdata']['djname']
		spdan = player['userdata']['spclass']
		dpdan = player['userdata']['dpclass']

	# count clear counts
	clearcount = {
		'noplay': 0,
		'failed': 0,
		'assist': 0,
		'easy': 0,
		'normal': 0,
		'hard': 0,
		'exhard': 0,
		'fullcombo': 0
	}
	for category in score:
		for x in category['songs']:
			clearcount['noplay'] = clearcount['noplay'] + (x['clear'] == 0)
			clearcount['failed'] = clearcount['failed'] + (x['clear'] == 1)
			clearcount['assist'] = clearcount['assist'] + (x['clear'] == 2)
			clearcount['easy'] = clearcount['easy'] + (x['clear'] == 3)
			clearcount['normal'] = clearcount['normal'] + (x['clear'] == 4)
			clearcount['hard'] = clearcount['hard'] + (x['clear'] == 5)
			clearcount['exhard'] = clearcount['exhard'] + (x['clear'] == 6)
			clearcount['fullcombo'] = clearcount['fullcombo'] + (x['clear'] == 7)

	return render_template('rankview.html', option=option_,
		user={'name': name, 'spdan': iidx.getdanstring(spdan),
			'spdannum':spdan, 'dpdan': iidx.getdanstring(dpdan), 'dpdannum': dpdan},
		clearcount=clearcount,
		datas=score)

def render_songlist(data, title, userjson):
	# parse web (get player json file)
	# TODO if no user required, just render it without clear graph
	player = jsondata.loadJSONurl(userjson)
	if (player == None or 'userdata' not in player or player['status'] != 'success'):
		print "userdata not found"
		abort(404)	# should show abort(404)
		return

	# create score data
	score = song.processCSV(player['musicdata'], data.RankCategory)

	return render_score(player, score, option)

#
# ------------------ customs (view) -------------------------
#

def render_SP12_7():
	#load from DB
	data = db.RankTable.query.filter_by(tablename='SP12_7')[0]
	title = "Beatmania IIDX SP lv.12 Hard Guage Rank"
	userjson = "http://json.iidx.me/kuna/%s/level/%d/" % ("sp", 12)
	return render_songlist(data, title, userjson)