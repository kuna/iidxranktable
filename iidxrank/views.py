#-*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import render, render_to_response
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.core.paginator import Paginator
import models
import settings

from update import jsondata
import rankpage as rp

import base64

####

def mainpage(request):
	notices = models.Board.objects.filter(title='notice').first().boardcomment_set
	return render(request, 'notice.html', {'notices': notices.order_by('-time')})

def userpage(request, username):
	# TODO: apart userpage from index. change index to search.
	return render(request, 'index.html', {'username': username})

def rankpage(request, username, diff, level):
	# check is argument valid
	diff = diff.upper()
	level = level.upper()
	ranktable = models.RankTable.objects.filter(tablename=diff+level).first()
	if (ranktable == None):
		return HttpResponseNotFound('<h1>Invalid table</h1>')

	# load player json data
	if (username == "!"):
		player = None
	else:
		userjson_url = "http://json.iidx.me/%s/%s/level/%d/" % (username, ranktable.type.lower(), ranktable.level)
		player = jsondata.loadJSONurl(userjson_url)
		if (player == None or 'userdata' not in player or player['status'] != 'success'):
			return HttpResponseNotFound('<h1>Invalid User, or Cannot connect to json.iidx.me</h1>')
	
	# compile user data to render score
	userinfo, songdata, pageinfo = rp.compile_data(ranktable, player, models.Song.objects)
	return render(request, 'rankview.html', {'score': songdata, 'user': userinfo, 'pageinfo': pageinfo})
	#return HttpResponse('rankpage - %s, %s, %s' % (username, diff, level))

# TODO not implemented, you should run update in shell directly.
def db_update(request):
	if not request.user.is_superuser:
		return HttpResponseNotFound('<h1>Forbidden</h1>')
	return HttpResponse("up-date page.")

def songcomment_all(request, page=1):
	songcomment_list = models.SongComment.objects.order_by('-time').all()
	paginator = Paginator(songcomment_list, 100)
	
	try:
		songcomments = paginator.page(page)
	except:
		return HttpResponseNotFound("invalid page")

	return render_to_response('songcomment_all.html', {"comments": songcomments})

# /iidx/songcomment/<ranktablename>/<songid(pk)>/
def songcomment(request, ranktablename, songid):
	# check is valid url
	ranktable = models.RankTable.objects.filter(tablename=ranktablename).first()
	song = models.Song.objects.filter(id=songid).first()
	if (ranktable == None or song == None):
		return HttpResponseNotFound("invalid id")

	# check admin
	attr = 0
	if (request.user.is_superuser):
		attr = 2
	# return message (mostly error)

	if (request.method == "POST"):
		message = ""
		ip = get_client_ip(request)
		password = request.POST["password"]
		# if no password, then make ip as password
		if (password == ""):
			password = ip

		if (request.POST["mode"] == "delete"):
			# delete comment
			comment_id = request.POST["id"]
			if (attr == 2):
				# admin can delete any comment
				comment = models.SongComment.objects.filter(id=comment_id).first()
			else:
				comment = models.SongComment.objects.filter(id=comment_id, password=password).first()

			if (not comment):
				message = "Wrong password"
			else:
				comment.delete()
				message = "Removed Comment"
		elif (request.POST["mode"] == "add"):
			# check argument is valid
			text = request.POST["text"]
			writer = request.POST["writer"]
			if (len(text) <= 5 or len(writer) <= 0):
				message = u"코멘트나 이름이 너무 짧습니다."
			if (models.BannedUser.objects.filter(ip=ip).count()):
				message = u"차단당한 유저입니다."

			if (message == ""):
				# add comment
				models.SongComment.objects.create(
					ranktable = ranktable,
					song= song,
					text = text,
					score = request.POST["score"],
					writer = writer,
					ip = ip,
					attr = attr,
					password = password,
				)
				# remember writer session
				request.session['writer'] = writer
				message = u"코멘트를 등록하였습니다."

		# add message to session
		request.session['message'] = message

		# after POST request, redirect to same view
		# (prevent sending same request)
		return HttpResponseRedirect(reverse("songcomment", args=[ranktablename, songid]))

	# fetch all comments & fill rank info
	comments = models.SongComment.objects.filter(ranktable=ranktable, song=song)
	rankitem = models.RankItem.objects.filter(rankcategory__ranktable=ranktable, song=song).first()
	boardinfo = {
		'songinfo': song,
		'rankinfo': rankitem,
		'ranktable': ranktable,
		'message': request.session.get('message', ''),
		'admin': attr == 2,
		'writer': request.session.get('writer', ''),
	}
	# clear message
	request.session['message'] = ''

	return render(request, 'songcomment.html', {'comments': comments.order_by('-time'), 'board': boardinfo})

# /iidx/board/<boardid>/<boardpage>
def board(request, boardid):
	# TODO
	return render(request, 'board.html', {'comments': comments, 'board': boardinfo})

# /iidx/selectmusic
def selectmusic(request):
	# all the other things will done in json & html
	return render_to_response('selectmusic.html')


# iidx/imgtl/
@csrf_exempt
def imgtl(request):
	if request.method != "POST":
		raise PermissionDenied

	filename = request.POST['name']
	pngdata = base64.decodestring(request.POST['base64'])
	print "got imgtl request: %s (%d byte)" % (request.POST['name'], len(pngdata))

	import requests
	import urllib2
	header = {'X-IMGTL-TOKEN': settings.imgtlkey}
	r = requests.post('https://api.img.tl/upload', data={'desc': '', 'filename': filename}, \
		files={'file': (filename, pngdata, 'application/octet-stream')}, headers=header)
	return HttpResponse(r.text)

# TODO: board url
