#-*- coding: utf-8 -*-
# start web server
from flask import Flask, render_template
import song, view
import env

from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper

import base64

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


app = Flask(__name__)

@app.route('/')
def main():
	return render_template('main.html')

def render_score(player, score, mode_, title_):
	def getdanstring(dan):
		if (dan == 1):
			return u"-"
		elif (dan == 2):
			return u"七級"
		elif (dan == 3):
			return u"六級"
		elif (dan == 4):
			return u"五級"
		elif (dan == 5):
			return u"四級"
		elif (dan == 6):
			return u"三級"
		elif (dan == 7):
			return u"二級"
		elif (dan == 8):
			return u"一級"
		elif (dan == 9):
			return u"初段"
		elif (dan == 10):
			return u"二段"
		elif (dan == 11):
			return u"三段"
		elif (dan == 12):
			return u"四段"
		elif (dan == 13):
			return u"五段"
		elif (dan == 14):
			return u"六段"
		elif (dan == 15):
			return u"七段"
		elif (dan == 16):
			return u"八段"
		elif (dan == 17):
			return u"九段"
		elif (dan == 18):
			return u"十段"
		elif (dan == 19):
			return u"皆伝"

	name = player['userdata']['djname']
	spdan = player['userdata']['spclass']
	dpdan = player['userdata']['dpclass']

	return render_template('common.html', mode=mode_, title=title_, \
		user={'name': name, 'spdan': getdanstring(spdan), 'spdannum':spdan, 'dpdan': getdanstring(dpdan), 'dpdannum': dpdan},\
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

	return render_score(player, score, "sp", "Beatmania IIDX SP lv.12 <span style='color:red;'>Hard Guage</span> Rank")

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
@crossdomain(origin='https://api.img.tl', headers='Content-Type')
def test():
	import json
	f = open('./data/test', 'rb')
	player = json.loads(f.read())
	f.close()

	data = song.getCSVdata("./data/dp.10.txt")
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

def init():
	if (env.TESTING):
		app.debug = True

if __name__ == '__main__':
	init()
	app.run(host='0.0.0.0', port=80)
