#-*- coding: utf-8 -*-
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import render, render_to_response
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.core.paginator import Paginator
import models
import iidxrank.models
import random
import datetime

import board.forms as forms

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

    # writable?
    writeable = board.permission == 0 or request.user.is_staff

    r =  render(request, 'list.html',
            {'posts': comments_page, 'board': board, 'status': status, 'writeable': writeable})
    clearMessage(request)
    return r

# /board/<boardname>/write/
def write(request, boardname):
    board = models.Board.objects.filter(title=boardname).first()
    if (board == None):
        raise Http404
    status = getBasicStatus(request)

    # writable?
    writeable = board.permission == 0 or request.user.is_staff
    if (not writeable):
        raise PermissionDenied

    if (request.method == "POST"):
        form = forms.PostForm(request.POST)
        ip = get_client_ip(request)
        # if no password, then make ip as password
        password  = form.data['password']
        if (password == ""):
            password = ip

        if (form.data['mode'] == "add"):
            # check argument is valid
            if (form.is_valid_with_ip(ip)):
                # session and message
                request.session['writer'] = form.data['writer']

                # add comment
                models.BoardPost.objects.create(
                        board = board,
                        title = form.data['title'],
                        text = form.data['text'],
                        writer = form.data['writer'],
                        tag = form.data['tag'],
                        attr = status['attr'],
                        ip = ip,
                        password = password,
                        )
                return HttpResponseRedirect(reverse("postlist", args=[boardname, 1]))
            else:
                request.session['message'] = form.errors.as_text().replace("\n","-")

    else:
        form = forms.PostForm(initial={
            'writer':status['writer']
            })

    r = render(request, 'edit.html',
            {'board': board, 'form': form})
    clearMessage(request)
    return r

# /board/modify/<postid>/
def modify(request, postid):
    post = models.BoardPost.objects.filter(id=postid).first()
    if (post == None):
        raise Http404
    status = getBasicStatus(request)
    board = post.board

    # writable?
    writeable = board.permission == 0 or request.user.is_staff
    if (not writeable):
        raise PermissionDenied

    if (request.method == "POST"):
        form = forms.PostForm(request.POST)
        ip = get_client_ip(request)
        if (form.is_valid_with_ip(ip, status['attr'], post.password)):
            mode = form.data["mode"]
            if (mode == "delete"):
                post.delete()
                request.session['message'] = "Removed Post."
            elif (mode == "modify"):
                post.title = form.data['title']
                post.writer = form.data['writer']
                post.tag = form.data['tag']
                post.text = form.data['text']
                post.save()
                request.session['message'] = "Modified Post."
                return HttpResponseRedirect(reverse("postview", args=[post.id,]))
            else:
                request.session['message'] = "Something unexpected happened."
            return HttpResponseRedirect(reverse("postlist", args=[boardname, 1]))
        else:
            request.session['message'] = form.errors.as_text().replace("\n","-")

    else:
        form = forms.PostForm(initial={
            'title': post.title,
            'writer': post.writer,
            'text': post.text,
            'mode': 'modify',
            })

    # return to edit window
    r = render(request, 'edit.html',
            {'board': board, 'post':post, 'form': form, 'edit': True})
    clearMessage(request)
    return r





# comment part
def comment_POST(request, status, post):
    if (post == None):
        request.session['message'] = u"An Internal error occured."
        return
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


# /board/view/<postid>/
def view(request, postid):
    # check is valid url
    post = models.BoardPost.objects.filter(id=postid).first()
    if (post == None):
        raise Http404
    status = getBasicStatus(request)
    status['page'] = 1  # TODO

    if (request.method == "POST"):
        comment_POST(request, status, post)

    # fetch all comments (which has no parents)
    comments = models.BoardComment.objects\
        .filter(post=post, parent=None)\
        .order_by('-time')

    r = render(request, 'view.html',
            {'comments': comments, 'post': post, 'board': post.board, 'status': status})
    clearMessage(request)
    return r






# songcomment parts

def songcomments(request, page=1):
    # check is valid url
    board = models.Board.objects.filter(title="songcomment").first()
    status = getBasicStatus(request)

    # fetch all posts (with pagination)
    posts = models.BoardPost.objects.filter(board=board).order_by('-time')
    comments_page = Paginator(posts.all(), 20).page(page)

    # writable?
    writeable = board.permission == 0 or request.user.is_staff

    r =  render(request, 'songcomments.html',
            {'posts': comments_page, 'board': board, 'status': status, 'writeable': writeable})
    clearMessage(request)
    return r

def songcomment(request, tag):
    board = models.Board.objects.get(title="songcomment")
    post = models.BoardPost.objects.filter(board=board, tag=tag).first()
    status = getBasicStatus(request)
    # find song and get song title
    # and prepare virtual posting object
    try:
        tablename, song_pkid = tag.rsplit("_",1)
        print song_pkid
        song = iidxrank.models.Song.objects.get(id=song_pkid)
    except Exception as e:
        # invalid item no.
        print e
        raise Http404

    # check out rankpage also.
    ranktable = iidxrank.models.RankTable.objects.filter(tablename=tablename).first()
    if (ranktable == None):
        rankpage = {'url': '#', 'name': u'(존재하지 않습니다)'}
    else:
        rankpage = {'url': '/!/'+tablename+'/detail/', 'name': ranktable.tabletitle}

    if (request.method == "POST"):
        if (post == None and checkValidText(request.POST["text"])):
            # create a post
            post = models.BoardPost.objects.create(
                board = board,
                title = u'%s (%s / %d)' % (song.songtitle, song.songtype, song.songlevel),
                text = u'아직 난이도 변경내역이 없습니다.',
                writer = 'Bot',
                tag = tag,
                attr = 2,
                ip = 'Bot',
                password = int(random.random()*100000),
                )
        if (post):
            # create a comment
            # by using common comment function
            comment_POST(request, status, post)
            # and, update post date to current one
            post.time = datetime.datetime.now()
            post.save()

    # anyway, return songcomment window
    if (post):
        comments = post.get_comments()
    else:
        comments = []
        post = {
            'title': u'%s (%s / %d)' % (song.songtitle, song.songtype, song.songlevel),
            'text': u'아직 의견이 없습니다.',
            'writer': 'Bot',
            'attr': 2,
            }
    r = render(request, 'songcomment.html', {
        'post': post, 'comments': comments, 'status':status, 'rankpage':rankpage
        })
    clearMessage(request)
    return r
