#-*- coding: utf-8 -*-
import thread
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, render_to_response
import models

# for update
from update import updatedb
from update import updateuser
from update import calculatedb
from update import db
from update import log
from update import parser_iidxme
from datetime import datetime

def checkAdmin(request):
	if not request.user.is_superuser:
		raise PermissionDenied

def checkStaff(request):
	if not request.user.is_staff:
		raise PermissionDenied

############################################

def index(request):
	checkAdmin(request)
	return render_to_response('update/index.html')

def status(request):
	checkStaff(request)
	return render_to_response('update/status.html')
def json_status(request):
	checkStaff(request)
	return JsonResponse({'status': 'success', 'logs': log.getLogs()})

###### generic updater (for staff)  ########
updating = False
def update_worker(func):
	global updating
	updating = True
	try:
		log.Print('initalize DB...')
		func()
		log.Print('finished. committing...')
	except Exception, e:
		import traceback
		log.Print(e)
		line = traceback.format_exc()
		log.Print(line)
	updating = False
def update(request, update):
	checkStaff(request)
	global updating
	if (updating):
		return JsonResponse({'status': '이미 업데이트 중입니다'})

	func = None
	if (update == 'song'):
		func = updatedb.update_iidxme
	elif (update == 'dp'):
		func = updatedb.update_DP
	elif (update == 'player'):
		func = updateuser.update_user
	elif (update == 'playrecord'):
		func = updateuser.update_user_information
	elif (update == 'calculateMCMC'):
		func = calculatedb.calc_MCMC
	elif (update == 'calculatesongrough'):
		func = calculatedb.calc_song_rough
	elif (update == 'calculatesongdetail'):
		func = calculatedb.calc_song_stable

	if (func == None):
		return JsonResponse({'status': '유효하지 않은 명령입니다'})
	else:
		log.Print("work: %s" % update)
		thread.start_new_thread(update_worker, (func,))
	return JsonResponse({'status': 'success'})

###### called when staff updates rankpage ######
def rankupdate(request):
	checkStaff(request)

	# get argument
	category_id = request.POST["category_id"]
	song_id = request.POST["song_id"]
	rankitem_id = request.POST["rankitem_id"]
	action = request.POST["action"]
	rankcategory = models.RankCategory.objects.get(pk=category_id)
	song = models.Song.objects.get(pk=song_id)

	# change(add) category
	# or delete rankitem
	if (action == "change"):
		if (not rankitem_id):
			models.RankItem.objects.create(
				rankcategory = rankcategory,
				song = song,
				info = ''
				)
		else:
			rankitem = models.RankItem.objects.get(pk=rankitem_id)
			rankitem.rankcategory = rankcategory
			rankitem.song = song
			rankitem.save()
	elif (action == "delete"):
		if (rankitem_id):
			rankitem = models.RankItem.objects.get(pk=rankitem_id)
			rankitem.delete();

	return JsonResponse({'status': 'success', 'action': action, 'song': song.songtitle, 'rankcategory': rankcategory.categoryname})

############################################
# user update
#
updating_user = False
updating_username = ""
last_update_time = 0
def update_player_worker(iidxmeid):
	global updating_user, updating_username
	updating_user = True
	updating_username = iidxmeid

	try:
		updateuser.update_single_user_by_name(iidxmeid)
		# commit first to get data in calculatedb
		db.commit()
	except Exception, e:
		log.Print("error occured during updateuser.update_single_user_by_name(%s)" % updating_user)

	try:
		calculatedb.calculate_player_by_name(iidxmeid)
		# must save it to DB right now to show right result
		db.commit()
	except Exception, e:
		log.Print("error occured during calculatedb.calculate_player_by_name(%s)" % updating_user)

	log.Print('finished %s' % iidxmeid)
	updating_user = False
	updating_username = ""

def json_update_player(request, username):
	try:
		player = models.Player.objects.get(iidxmeid=username)
		if (not player.isRefreshable()):
			return JsonResponse({'status': '업데이트는 24시간마다 가능합니다'})
		else:
			if (updating_user or updating):
				return JsonResponse({'status': '현재 서버가 바쁩니다. 잠시 후에 시도해 주세요.'})

			# make a new thread (worker)
			thread.start_new_thread(update_player_worker, (username,))

			return JsonResponse({'status': 'success'})
	except Exception, e:
		import traceback, sys
		print e
		traceback.print_exc(file= sys.stdout)
		user_info = parser_iidxme.parse_userinfo(username)
		if (user_info == None):
			return JsonResponse({'status': 'not existing user'})
		else:
			log.Print('creating new user %s ...' % username)
			updateuser.add_user(user_info)
			db.commit()	# MUST do commit!
			# try again recursively
			return json_update_player(request, username)

def json_update_player_status(request, username):
	return JsonResponse({'status': 'success', 'updating':(updating_username == username)})
