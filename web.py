# start web server
from flask import Flask, render_template
import song, view
import env

app = Flask(__name__)

@app.route('/')
def main():
	return render_template('main.html')

@app.route('/iidx/sp/<user>/<int:level>')
def iidxsp(user, level):
	player = song.getSPinfo(user, level)
	return render_template('common.html', datas=player.musicdata)

def init():
	if (env.TESTING):
		app.debug = True

if __name__ == '__main__':
	init()
	app.run(host='127.0.0.1', port=80)
