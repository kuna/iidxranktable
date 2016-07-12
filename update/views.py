from django.shortcuts import render
from django.http import JsonResponse
import celery

def update_user(iidxmeid):
    celery.update_user.delay(iidxmeid)
    return JsonResponse({'message': 'OK'})

# TODO
def update_user_status(iidxmeid):
    return JsonResponse({'message': 'TODO', 'status': 1})
