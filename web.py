#-*- coding: utf-8 -*-
# start web server
from flask import Flask, render_template, abort
import song, view
import env

from flask import make_response, request, current_app

import base64
import iidx

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')

def render_score(player, score, mode_, title_):
	name = player['userdata']['djname']
	spdan = player['userdata']['spclass']
	dpdan = player['userdata']['dpclass']

	return render_template('common.html', mode=mode_, title=title_, \
		user={'name': name, 'spdan': iidx.getdanstring(spdan), 'spdannum':spdan, 'dpdan': iidx.getdanstring(dpdan), 'dpdannum': dpdan},\
		datas=score)

@app.route('/iidx/sp/<user>/12.7')
def iidxsp127(user):
	# clddal.kr
	# parse web
	player = song.getiidxinfo(user, 'sp', 12)
	if ('userdata' not in player or player['status'] != 'success'):
		abort(404)

	# load data file
	data = song.getCSVdata("./data/sp.12.7.txt")

	# create score data
	score = song.processCSV(player['musicdata'], data)

	return render_score(player, score, "sp", "Beatmania IIDX SP lv.12 Rank")

@app.route('/iidx/sp/<user>/12')
def iidxsp12(user):
	# http://nozomi.2ch.sc/test/read.cgi/otoge/1405129623/
	# parse web
	player = song.getiidxinfo(user, 'sp', 12)
	if ('userdata' not in player or player['status'] != 'success'):
		abort(404)

	# load data file
	data = song.getCSVdata("./data/sp.12.txt")

	# create score data
	score = song.processCSV(player['musicdata'], data)

	return render_score(player, score, "sp", "Beatmania IIDX SP lv.12 Hard Guage Rank")

@app.route('/iidx/dp/<user>/12')
def iidxdp12(user):
	# parse web
	player = song.getiidxinfo(user, 'dp', 12)
	if ('userdata' not in player or player['status'] != 'success'):
		abort(404)

	# load data file
	data = song.getCSVdata("./data/dp.12.txt")

	# create score data
	score = song.processCSV(player['musicdata'], data)

	return render_score(player, score, "dp", "Beatmania IIDX DP lv.12 Rank")

@app.route('/iidx/dp/<user>/11')
def iidxdp11(user):
	# parse web
	player = song.getiidxinfo(user, 'dp', 11)
	if ('userdata' not in player or player['status'] != 'success'):
		abort(404)

	# load data file
	data = song.getCSVdata("./data/dp.11.txt")

	# create score data
	score = song.processCSV(player['musicdata'], data)

	return render_score(player, score, "dp", "Beatmania IIDX DP lv.11 Rank")

@app.route('/iidx/dp/<user>/10')
def iidxdp10(user):
	# parse web
	player = song.getiidxinfo(user, 'dp', 10)
	if ('userdata' not in player or player['status'] != 'success'):
		abort(404)

	# load data file
	data = song.getCSVdata("./data/dp.10.txt")

	# create score data
	score = song.processCSV(player['musicdata'], data)

	return render_score(player, score, "dp", "Beatmania IIDX DP lv.10 Rank")

@app.route('/test')
def test():
	import json
	f = open('./data/test', 'rb')
	player = json.loads(f.read())
	f.close()

	data = song.getCSVdata("./data/test.dp.10.txt")
	score = song.processCSV(player['musicdata'], data)

	return render_score(player, score, "dp", "Beatmania IIDX SP lv.12 Hard Guage Rank")

@app.route('/imgtl', methods=['POST'])
def imgtl():
	print "got imgtl request: %s" % request.form['name']
	filename = request.form['name']
	pngdata = base64.decodestring(request.form['base64'])

	import requests
	import urllib2
	header = {'X-IMGTL-TOKEN': '87b8e0cac380e5cfc190101ff70ab6a1'}
	r = requests.post('https://api.img.tl/upload', data={'desc': '', 'filename': filename}, \
		files={'file': pngdata}, headers=header)
	"""print r.status_code
	print r.text
	f = open('test.png', 'wb')
	f.write(pngdata)
	f.close()"""
	return r.text

@app.errorhandler(404)
def not_found(error):
	return render_template('404.html'), 404

def init():
	if (env.TESTING):
		app.debug = True

if __name__ == '__main__':
	init()
	app.run(host='0.0.0.0', port=1100)
