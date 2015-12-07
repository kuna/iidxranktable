#-*- coding: utf-8 -*-
import thread
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import models
from update import updatedb

# for update
from update import updateuser
from update import calculatedb
from update import db

def checkAdmin(request):
	if not request.user.is_superuser:
		raise PermissionDenied

def index(request):
	checkAdmin(request)
	return render(request, 'update.html')

def recentStatus(request):
	checkAdmin(request)
	lines = updatedb.getRecentMsgs()
	return JsonResponse({'messages': lines})

def sendMessage(request, message):
	checkAdmin(request)
	updatedb.sendMessage(message)
	return JsonResponse({'status': 'success'})

# argument: category_id, song_id
def rankupdate(request):
	checkAdmin(request)

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

# returns JSON
def startUpdate(request, update):
	checkAdmin(request)
	if (update == ""):
		updatedb.dosomething;
		return JsonResponse({'status': 'success'})
	else:
		return JsonResponse({'status': 'invalid action'})


############################################
# user update
#
updating_user = False
def update_player_worker(iidxmeid):
	global updating_user
	updating_user = True
	db_session = db.init_db()

	updateuser.update_single_user_by_name(iidxmeid)
	calculatedb.calculate_player_by_name(iidxmeid)

	db_session.commit()
	db_session.remove()
	print 'finished %s' % iidxmeid
	updating_user = False

def json_update_player(request, username):
	try:
		player = models.Player.objects.get(iidxmeid=username)
		if (not player.isRefreshable()):
			return JsonResponse({'status': '업데이트는 24시간마다 가능합니다'})
		else:
			if (updating_user):
				return JsonResponse({'status': '현재 서버가 바쁩니다. 잠시 후에 시도해 주세요.'})

			# make a new thread (worker)
			thread.start_new_thread(update_player_worker, (username,))

			return JsonResponse({'status': 'success'})
	except Exception, e:
		import traceback, sys
		print e
		traceback.print_exc(file= sys.stdout)
		return JsonResponse({'status': 'not existing user'})
