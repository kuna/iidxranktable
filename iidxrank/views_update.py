from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
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

# returns JSON
def startUpdate(request, update):
	checkAdmin(request)
	if (update == ""):
		updatedb.dosomething;
		return JsonResponse({'status': 'success'})
	else:
		return JsonResponse({'status': 'invalid action'})

