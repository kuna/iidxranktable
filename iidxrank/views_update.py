from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import models
from update import updatedb

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

