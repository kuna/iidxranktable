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

@app.route('/iidx/<user>/sp/12.7')
def iidxsp127(user):
	return rankpage.render_table("SP12_7", user)

@app.route('/iidx/<user>/sp/12')
def iidxsp12(user):
	return rankpage.render_table("SP12_2ch", user)

@app.route('/iidx/<user>/sp/11')
def iidxsp11(user):
	return rankpage.render_table("SP11", user)

@app.route('/iidx/<user>/sp/10')
def iidxsp10(user):
	return rankpage.render_table("SP10", user)

@app.route('/iidx/<user>/sp/9')
def iidxsp9(user):
	return rankpage.render_table("SP9", user)

@app.route('/iidx/<user>/sp/8')
def iidxsp8(user):
	return rankpage.render_table("SP8", user)

@app.route('/iidx/<user>/sp/12N')
def iidxsp12N(user):
	return rankpage.render_table("SP12N", user)

@app.route('/iidx/<user>/sp/11N')
def iidxsp11N(user):
	return rankpage.render_table("SP11N", user)

@app.route('/iidx/<user>/sp/10N')
def iidxsp10N(user):
	return rankpage.render_table("SP10N", user)

@app.route('/iidx/<user>/sp/9N')
def iidxsp9N(user):
	return rankpage.render_table("SP9N", user)

@app.route('/iidx/<user>/sp/8N')
def iidxsp8N(user):
	return rankpage.render_table("SP8N", user)


@app.route('/iidx/<user>/dp/12')
def iidxdp12(user):
	return rankpage.render_table("DP12", user)

@app.route('/iidx/<user>/dp/11')
def iidxdp11(user):
	return rankpage.render_table("DP11", user)

@app.route('/iidx/<user>/dp/10')
def iidxdp10(user):
	return rankpage.render_table("DP10", user)

@app.route('/iidx/<user>/dp/9')
def iidxdp9(user):
	return rankpage.render_table("DP9", user)

@app.route('/iidx/<user>/dp/8')
def iidxdp8(user):
	return rankpage.render_table("DP8", user)

@app.route('/iidx/<user>/dp/7')
def iidxdp7(user):
	return rankpage.render_table("DP7", user)

@app.route('/iidx/<user>/dp/6')
def iidxdp6(user):
	return rankpage.render_table("DP6", user)

#####################################################

@app.route('/iidx/<user>/')
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
