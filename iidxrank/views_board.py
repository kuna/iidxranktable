#-*- coding: utf-8 -*-
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import render, render_to_response
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.core.paginator import Paginator
import models

def get_client_ip(request):
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		ip = x_forwarded_for.split(',')[0]
	else:
		ip = request.META.get('REMOTE_ADDR')
	return ip


# /iidx/songcomment/<ranktablename>/<songid(pk)>/
def songcomment(request, ranktablename, songid):
	# check is valid url
	ranktable = models.RankTable.objects.filter(tablename=ranktablename).first()
	song = models.Song.objects.filter(id=songid).first()
	if (ranktable == None or song == None):
		raise Http404

	# check admin
	attr = 0
	if (request.user.is_staff):
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
                        for banword in models.BannedWord.objects.all():
                            if banword.word in text:
				message = u"코멘트에 사용할 수 없는 단어가 들어가 있습니다."
                                break
			ip_ban = ".".join(ip.split(".")[:3])
			if (models.BannedUser.objects.filter(ip=ip_ban).count()):
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
def board(request, boardid, boardpage=1):
	# check is valid url
	board = models.Board.objects.filter(id=boardid).first()
	if (board == None):
		raise Http404

	# check admin
	is_admin = request.user.is_superuser
	attr = 0
	if (is_admin):
		attr = 2

	# TODO make this tidy
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
				comment = models.BoardComment.objects.filter(id=comment_id).first()
			else:
				comment = models.BoardComment.objects.filter(id=comment_id, password=password).first()

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
				models.BoardComment.objects.create(
					board = board,
					text = text,
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
		return HttpResponseRedirect(reverse("board", args=[boardid, boardpage]))

	# fetch all comments & fill rank info
	comments = models.BoardComment.objects.filter(board=board).order_by('-time')
	comments_page = Paginator(comments.all(), 100).page(boardpage)
	status = {
		'iswritable': not (board.permission > 0 and not is_admin),
		'isadmin': is_admin,
		'message': request.session.get('message', ''),
		'writer': request.session.get('writer', ''),
	}
	# clear message
	request.session['message'] = ''

	return render(request, 'board.html', {'comments': comments_page, 'board': board, 'status': status})
