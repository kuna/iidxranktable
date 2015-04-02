#-*- coding: utf-8 -*-
# start web server
from flask import Flask, render_template, abort
import song, view
import env, private

from flask import make_response, request, current_app

import base64
import iidx
import jsondata

app = Flask(__name__)

def render_score(player, score, mode_, title_, titlehtml_):
	name = player['userdata']['djname']
	spdan = player['userdata']['spclass']
	dpdan = player['userdata']['dpclass']

	return render_template('rankview.html', mode=mode_, title=title_, titlehtml=titlehtml_, \
		user={'name': name, 'spdan': iidx.getdanstring(spdan), 'spdannum':spdan, 'dpdan': iidx.getdanstring(dpdan), 'dpdannum': dpdan},\
		datas=score)

def render_songlist(optionpath, user):
	# read option json
	option = jsondata.loadJSONfile(optionpath)

	# parse web (get player json file)
	player = None
	if (user == None):
		data = jsondata.loadJSONfile(option['jsonfile'])
	else:
		player = song.getiidxinfo(user, option['type'], option['level'])

	if (player == None or 'userdata' not in player or player['status'] != 'success'):
		abort(404)	# should show abort(404)
		return

	# load data file
	data = song.getCSVdata(option['datafile'])
	if (data == None):
		abort(404)	# 404
		return

	# create score data
	score = song.processCSV(player['musicdata'], data)

	return render_score(player, score, option['type'], option['title'], option['titlehtml'])

#####################################################

@app.route('/iidx/sp/<user>/12')
def iidxsp12(user):
	return render_songlist("./data/sp.12.json", user)

@app.route('/iidx/sp/<user>/12.7')
def iidxsp127(user):
	return render_songlist("./data/sp.12.7.json", user)

@app.route('/iidx/sp/<user>/11')
def iidxsp11(user):
	return render_songlist("./data/sp.11.json", user)

@app.route('/iidx/sp/<user>/10')
def iidxsp10(user):
	return render_songlist("./data/sp.10.json", user)


@app.route('/iidx/dp/<user>/12')
def iidxdp12(user):
	return render_songlist("./data/dp.12.json", user)

@app.route('/iidx/dp/<user>/11')
def iidxdp11(user):
	return render_songlist("./data/dp.11.json", user)

@app.route('/iidx/dp/<user>/10')
def iidxdp10(user):
	return render_songlist("./data/dp.10.json", user)

#####################################################

@app.route('/iidx/<user>')
def userpage(user):
	return render_template('index.html', username=user)

@app.route('/iidx')
@app.route('/')
def index():
	return render_template('index.html')

#####################################################

@app.route('/test')
def test():
	return render_songlist("./data/dp.10.json")

#####################################################

@app.route('/imgtl', methods=['POST'])
def imgtl():
	print "got imgtl request: %s" % request.form['name']
	filename = request.form['name']
	pngdata = base64.decodestring(request.form['base64'])

	import requests
	import urllib2
	header = {'X-IMGTL-TOKEN': private.imgtlkey}
	r = requests.post('https://api.img.tl/upload', data={'desc': '', 'filename': filename}, \
		files={'file': (filename, pngdata, 'application/octet-stream')}, headers=header)
	return r.text

#####################################################

@app.errorhandler(404)
def not_found(error):
	return render_template('404.html'), 404

def init():
	if (env.TESTING):
		print 'currently debugging mode.'
		app.debug = True

if __name__ == '__main__':
	init()
	app.run(host='127.0.0.1', port=1100)
