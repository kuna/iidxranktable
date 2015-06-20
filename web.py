#-*- coding: utf-8 -*-
# start web server
from flask import Flask, render_template, abort
import env, private

from flask import make_response, request, current_app

import base64
import rankpage
import db

app = Flask(__name__)

#####################################################

@app.route('/iidx/sp/<user>/12.7')
def iidxsp127(user):
	return rankpage.render_songlist("./data/sp.12.7.json", user)

@app.route('/iidx/sp/<user>/12')
def iidxsp12(user):
	return rankpage.render_songlist("./data/sp.12.json", user)

@app.route('/iidx/sp/<user>/11')
def iidxsp11(user):
	return rankpage.render_songlist("./data/sp.11.json", user)

@app.route('/iidx/sp/<user>/10')
def iidxsp10(user):
	return rankpage.render_songlist("./data/sp.10.json", user)


@app.route('/iidx/dp/<user>/12')
def iidxdp12(user):
	return rankpage.render_songlist("./data/dp.12.json", user)

@app.route('/iidx/dp/<user>/11')
def iidxdp11(user):
	return rankpage.render_songlist("./data/dp.11.json", user)

@app.route('/iidx/dp/<user>/10')
def iidxdp10(user):
	return rankpage.render_songlist("./data/dp.10.json", user)



#@app.route('/iidx/sp/12.7')
#def iidxsp127(user):
#	return rankpage.render_songlist("./data/sp.12.7.json", None)


@app.route('/test')
def test():
	return rankpage.render_songlist("./data/dp.10.json")

#####################################################

@app.route('/iidx/<user>')
def userpage(user):
	return render_template('index.html', username=user)

@app.route('/iidx/')
@app.route('/iidx')
@app.route('/')
def index():
	return render_template('notice.html')

#####################################################

@app.route('/imgtl', methods=['POST'])
def imgtl():
	filename = request.form['name']
	pngdata = base64.decodestring(request.form['base64'])
	print "got imgtl request: %s (%d byte)" % (request.form['name'], len(pngdata))

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
	db_session = db.init_db()
	app.run(host='127.0.0.1', port=1100)
	db_session.remove()
