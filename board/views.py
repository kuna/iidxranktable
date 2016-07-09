#-*- coding: utf-8 -*-
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import render, render_to_response
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.core.paginator import Paginator
import models

# common functions
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def getBasicStatus(request):
    # check admin
    is_admin = request.user.is_superuser
    attr = 0
    if (is_admin):
        attr = 2

    # status
    status = {
            #'iswritable': not (board.permission > 0 and not is_admin),
            'isadmin': is_admin,
            'message': request.session.get('message', ''),
            'writer': request.session.get('writer', ''),
            'attr': attr,
            }
    
    return status

def clearMessage(request):
    request.session['message'] = ''

def checkValidation(writer, ip, text):
    message = None
    if (len(text) <= 5 or len(writer) <= 0):
        message = u"코멘트나 이름이 너무 짧습니다."
    for banword in models.BannedWord.objects.all():
        if banword.word in text:
            message = u"코멘트에 사용할 수 없는 단어/태그가 들어가 있습니다."
            break
    if (models.BannedUser.objects.filter(ip=ip).count()):
        message = u"차단당한 유저입니다."

    if (message == None):
        return (True, u"코멘트를 등록하였습니다.")
    else:
        return (False, message)
# common function end





# /board/<boardid>/<boardpage>
def list(request, boardname, page=1):
    # check is valid url
    board = models.Board.objects.filter(title=boardname).first()
    if (board == None):
        raise Http404
    status = getBasicStatus(request)

    # fetch all posts (with pagination)
    posts = models.BoardPost.objects.filter(board=board).order_by('-time')
    comments_page = Paginator(posts.all(), 20).page(page)

    r =  render(request, 'list.html',
            {'posts': comments_page, 'board': board, 'status': status})
    clearMessage(request)
    return r

# /board/<boardname>/write/
def write(request, boardname):
    board = models.Board.objects.filter(title=boardname).first()
    if (board == None):
        raise Http404
    status = getBasicStatus(request)

    if (request.method == "POST"):
        ip = get_client_ip(request)
        password = request.POST["password"]
        # if no password, then make ip as password
        if (password == ""):
            password = ip

        if (request.POST["mode"] == "add"):
            # check argument is valid
            title = request.POST["title"]
            text = request.POST["text"]
            tag = request.POST["tag"]
            writer = request.POST["writer"]
            v = checkValidation(ip, writer, text)
            if (v[0]):
                # add comment
                models.BoardPost.objects.create(
                        board = board,
                        title = title,
                        text = text,
                        writer = writer,
                        tag = tag,
                        attr = status['attr'],
                        ip = ip,
                        password = password,
                        )
            # remember writer session
            request.session['writer'] = writer
            message = v[1]

        # add message to session
        request.session['message'] = message

        # after POST request, redirect to same view
        # (prevent sending same request)
        return HttpResponseRedirect(reverse("postlist", args=[boardname, 1]))
    else:
        post = {
                'title': '',
                'writer': '',
                'tag': '',
                'text': '',
                }
        r = render(request, 'edit.html',
                {'board': board, 'status': status, 'post': post})
        clearMessage(request)
        return r

# /board/modify/<postid>/
def modify(request, postid):
    post = models.BoardPost.objects.filter(id=postid).first()
    if (post == None):
        raise Http404
    status = getBasicStatus(request)
    board = post.board

    if (request.method == "POST"):
        if (request.POST["mode"] == "delete"):
            password = request.POST["password"]
            if (post.password == password or status['attr'] == 2):
                post.delete()
                message = "Removed Post"
            else:
                message = "Wrong password"
            return HttpResponseRedirect(reverse("postlist", args=[board.title, 1]))
        elif (request.POST["mode"] == "modify"):
            password = request.POST["password"]
            writer = request.POST["writer"]
            text = request.POST["text"]
            v = checkValidation(ip, writer, text)

            # to stay data remaining
            post.title = request.POST["title"]
            post.text = request.POST["text"]
            post.tag = request.POST["tag"]
            post.writer = request.POST["writer"]
            if (v[0]):
                if (post.password == password or status['attr'] == 2):
                    post.save()
                    message = "Modified Post"
                    return HttpResponseRedirect(reverse("postview", args=[post.id,]))
                else:
                    post. 
                    message = "Wrong password"
            else:
                message = v[1]

    # failed to edit, or normal edit window
    r = render(request, 'edit.html',
            {'board': board, 'status': status, 'post': post, 'edit': True})
    return r


# /board/view/<postid>/
def view(request, postid):
    # check is valid url
    post = models.BoardPost.objects.filter(id=postid).first()
    if (post == None):
        raise Http404
    status = getBasicStatus(request)
    status['page'] = 1  # TODO

    # fetch all comments (which has no parents)
    comments = models.BoardComment.objects\
        .filter(post=post, parent=None)\
        .order_by('-time')

    r = render(request, 'view.html',
            {'comments': comments, 'post': post, 'board': post.board, 'status': status})
    clearMessage(request)
    return r

# /board/comment/<postid>/
def comment(request, postid):
    # check is valid url
    post = models.BoardPost.objects.filter(id=postid).first()
    if (post == None):
        raise Http404
    status = getBasicStatus(request)

    # only process POST request
    if (request.method == "POST"):
        if (request.POST['mode'] == "add"):
            parent_comment = int(request.POST["parent"])
            if (parent_comment == -1):
                parent = None
            else:
                parent = models.BoardComment.objects.get(id=parent_comment)
            writer = request.POST['writer']
            ip = get_client_ip(request)
            password = request.POST["password"]
            # if no password, then make ip as password
            if (password == ""):
                password = ip
            text = request.POST['text']
            r = checkValidation(writer, ip, text)
            request.session['message'] = r[1]
            if (r[0]):
                # add comment
                models.BoardComment.objects.create(
                        post = post,
                        parent = parent,
                        text = text,
                        writer = writer,
                        tag = '',
                        password = password,
                        attr = status['attr'],
                        ip = ip,
                        )
            # remember writer session
            request.session['writer'] = writer
        elif (request.POST['mode'] == "delete"):
            cmtid = request.POST['id']
            password = request.POST['password']
            ip = get_client_ip(request)
            # if no password, then make ip as password
            if (password == ""):
                password = ip
            cmtobj = models.BoardComment.objects.get(id=cmtid)
            if (cmtobj.password == password or status['attr'] == 2):
                cmtobj.delete()
                request.session['message'] = u"댓글을 삭제하였습니다."
            else:
                request.session['message'] = u"패스워드가 틀렸습니다."
        return HttpResponseRedirect(reverse("postview", args=[postid,]))
    else:
        raise Http404
