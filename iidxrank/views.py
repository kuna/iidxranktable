from django.http import HttpResponse
from django.shortcuts import render
import models

#
# -*- encode: utf8 -*-

def test(request):
    return HttpResponse('test')

def mainpage(request):
	# TODO: is all method bad?
	notices = models.Board.objects.filter(title='notice').all()[0].boardcomment_set
	return render(request, 'notice.html', {'notices': notices.order_by('-time')})

def userpage(request, username):
	# TODO: apart userpage from index. change index to search.
	return render(request, 'index.html', {'username': username})

def rankpage(request, username, diff, level):
	# check is argument valid
	diff = diff.lower()
	level = level.upper()
	return HttpResponse('rankpage - %s, %s, %s' % (username, diff, level))

# TODO: imgtl url
# TODO: board url
