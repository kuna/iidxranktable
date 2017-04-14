#-*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.clickjacking import xframe_options_exempt
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import models
import forms
import board.models
import settings

import rankpage as rp
import iidx
import json
import views_json
import base64

import update.parser_iidxme as iidxme



def checkValidPlayer(player):
    return not (player == None or 
        'userdata' not in player or 
        player['status'] != 'success')

def mainpage(request):
    # get first notice
    notice_board = board.models.Board.objects.get(title='notice')
    post = notice_board.posts.order_by('-time').first()
    # get recent 3 freetalk
    freetalk_board = board.models.Board.objects.get(title='freetalk')
    freetalk = freetalk_board.posts.order_by('-time')[:5]
    comments = board.models.BoardComment.objects.order_by('-time')[:5]
    votes = []
    return render(request, 'index.html', {
        'hidesearch': True, 'mobileview':True,
        'noticepost': post,
        'freetalk': freetalk,
        'comments': comments,
        'votes': votes,
        })

def userjson(request, username="!"):
    j = {}
    if (username != "!"):
        j = iidxme.parse_iidxme_http("http://iidx.me/%s/sp/level/12" % username)
    return JsonResponse(j)

def userpage(request, username="!"):
    if (username == "!"):
        # make dummy data
        player = None
    else:
        # check recent json to get player info
        #userjson_url = "http://json.iidx.me/%s/recent/" % username
        #player = jsondata.loadJSONurl(userjson_url)
        userpage_url = "http://iidx.me/%s/recent/" % username
        player = iidxme.parse_iidxme_http(userpage_url)
        if (not checkValidPlayer(player)):
            # invalid user!
            raise Http404
    playerinfo = rp.getUserInfo(player, username)
    return render(request, 'user/userpage.html', {'userinfo': playerinfo})

# common for rankpage
def retrieve_userdata(request, username, tablename):
    # check is argument valid
    tablename = tablename.upper()
    try:
        ranktable = models.RankTable.objects.get(tablename=tablename)
    except:
        # invalid table!
        raise Http404

    # load player json data
    if (username == "!"):
        # load player information from DB
        player = None
        if (request.user.is_authenticated()):
            pobj = models.Player.objects.filter(user=request.user).first()
            if (pobj):
                player = rp.get_player_data(pobj, ranktable)
    else:
        #userjson_url = "http://json.iidx.me/%s/%s/level/%d/" % (username, ranktable.type.lower(), ranktable.level)
        #player = jsondata.loadJSONurl(userjson_url)
        userpage_url = "http://iidx.me/%s/%s/level/%d/" % (username, ranktable.type.lower(), ranktable.level)
        player = iidxme.parse_iidxme_http(userpage_url)
        if (not checkValidPlayer(player)):
            # invalid user!
            raise Http404

    # compile user data to render score
    userinfo, songdata, pageinfo = rp.compile_data(ranktable, player, models.Song.objects)
    userinfo['title'] = pageinfo['title']
    userinfo['iidxmeid'] = username
    tabledata = {
        'info': userinfo,
        'categories': songdata
        }

    return {'score': songdata, 
        'ranktable': tabledata,
        'userinfo': userinfo, 
        'pageinfo': pageinfo}

"""
def rankpage(request, username="!", tablename="SP12"):
    d = retrieve_userdata(request, username, tablename)
    tabledata = d['ranktable']
    del d['ranktable']
    d['tabledata_json'] = json.dumps(tabledata)
    return render(request, 'user/rankview.html', d)
"""
def rankpage(request, username="!", tablename="SP12"):
    table = rp.get_ranktable(tablename)
    if (table == None):
        raise Http404
    player = None
    if (username == "!"):
        player = rp.get_player_from_request(request)
        pdata = rp.get_pdata_from_player(player,table)
    else:
        #userjson_url = "http://json.iidx.me/%s/%s/level/%d/" % (username, table.type.lower(), table.level)
        #iidxme_data = jsondata.loadJSONurl(userjson_url)
        userpage_url = "http://iidx.me/%s/%s/level/%d/" % (username, table.type.lower(), table.level)
        iidxme_data = iidxme.parse_iidxme_http(userpage_url)
        if (not checkValidPlayer(iidxme_data)):
            raise Http404
        pdata = rp.get_pdata_from_iidxme(iidxme_data,table)
    # only session authorized user can edit table.
    if (player):
        pdata['editable']=True
    else:
        pdata['editable']=False
    # append additional data
    pdata['tabledata_json'] = rp.serialize_ranktable(pdata)
    return render(request, 'user/rankview.html', pdata)

"""
def detailpage(request, username="!", tablename="SP12"):
    d = retrieve_userdata(username, tablename)
    return render(request, 'user/detailview.html', d)
"""

def ranktable(request, username="!", tablename="SP12"):
    d = retrieve_userdata(request, username, tablename)
    return render(request, 'ranktable.html', d)

def rankjson(request, username="!", tablename="SP12"):
    d = retrieve_userdata(request, username, tablename)
    return JsonResponse(d)

def rankedit(request, tablename):
    tablename = tablename.upper()

    # only admin can access it
    # TODO
    
    # in case of POST? -> return JSON result
    if (request.method == "POST"):
        return views_json.json_rankedit(request)
    
    # check is valid table
    ranktable = models.RankTable.objects.filter(tablename=tablename).first()
    if (ranktable == None):
        raise Http404
    # compile table data
    userinfo, songdata, pageinfo = rp.compile_data(ranktable, None, models.Song.objects, False)
    return render(request, 'rankedit.html', { 'songdata': songdata, 'tableid': ranktable.id, 'pageinfo': pageinfo })


def songcomment_all(request, page=1):
    songcomment_list = models.SongComment.objects.order_by('-time').all()
    paginator = Paginator(songcomment_list, 100)

    try:
        songcomments = paginator.page(page)
    except:
        # invalid pagenation!
        raise Http404

    return render(request, 'recentcomment.html', {"comments": songcomments})


# /iidx/musiclist
#@xframe_options_exempt
def musiclist(request):
    # all the other things will done in json & html
    return render('musiclist.html')

# /iidx/(username)/recommend/
def recommend(request, username):
    userjson_url = "http://json.iidx.me/%s/recent/" % username
    player = jsondata.loadJSONurl(userjson_url)
    if (not checkValidPlayer(player)):
        raise Http404
    userinfo = rp.getUserInfo(player, username)
    return render('user/recommend.html', {"userinfo": userinfo})

# /iidx/(username)/skillrank
def skillrank(request, username):
    userjson_url = "http://json.iidx.me/%s/recent/" % username
    player = jsondata.loadJSONurl(userjson_url)
    if (not checkValidPlayer(player)):
        raise Http404
    userinfo = rp.getUserInfo(player, username)
    return render('user/skillrank.html', {"userinfo": userinfo})

# /iidx/!/songrank/
def songrank(request):
    return render('songrank.html')

# /iidx/!/userrank/
def userrank(request):
    return render('userrank.html')


"""
user related part
"""

# /!/login/
login_django = login
def login(request):
    if (request.user.is_authenticated()):
        return redirect('main')
    if (request.method == "POST"):
        form = forms.LoginForm(request.POST)
        if (form.is_valid()):
            user = authenticate(username=form.data['id'], password=form.data['password'])
            login_django(request, user)
            return redirect('main')
    else:
        form = forms.LoginForm()

    return render(request, 'user/login.html', {'form': form})

# /!/join/
def join(request):
    if (request.user.is_authenticated()):
        return redirect('main')
    if (request.method == "POST"):
        form = forms.JoinForm(request.POST)
        if (form.is_valid()):
            user = User.objects.create_user(
                    username=form.data['id'],
                    email=form.data['email'],
                    password=form.data['password'])
            user = authenticate(username=form.data['id'], password=form.data['password'])
            login_django(request, user)
            return redirect('main')
    else:
        form = forms.JoinForm()
    return render(request, 'user/join.html', {'form': form})

# /!/logout/
logout_django = logout
def logout(request):
    logout_django(request)
    return redirect('main')

# /!/withdraw/
def withdraw(request):
    if (request.user.is_superuser):
        raise Exception("Superuser CANNOT withdraw!")
    if (not request.user.is_authenticated()):
        return redirect('login')
    if (request.method == "POST"):
        form = forms.WithdrawForm(request.POST)
        if (form.is_valid()):
            user = request.user
            user.delete()
            logout_django(request)
            return redirect('main')
    else:
        form = forms.WithdrawForm(initial={'id': request.user.username})
    return render(request, 'user/withdraw.html', {'form': form})

# JSON
# /!/modify/
def modify(request):
    if (not request.user.is_authenticated()):
        return JsonResponse({'code': 1, 'message': 'please log in'})
    user = request.user
    player = models.Player.objects.get(user=user)
    if (player == None):
        player = models.Player.objects.create(
                iidxmeid='',
                iidxid='-',
                iidxnick=user.username,
                user=user
                )
    action = request.GET.get('action', '')
    v = request.GET.get('v', '')
    if (action == 'record'):
        try:
            lst = json.loads(v)
            for l in lst:
                sid = int(l['sid'])
                song = models.Song.objects.get(id=sid)
                pr = models.PlayRecord.objects.get_or_create(song=song,player=player)
                pr.playclear = int(l['clear'])
                pr.playscore = int(l['score'])
                pr.save()
        except Exception as e:
            return JsonResponse({'code': 1, 'message': 'Invalid Song modification'})
    if (action == 'recorddelete'):
        try:
            sid = int(v)
            song = models.Song.objects.get(id=sid)
            pr = models.PlayRecord.objects.filter(song=song,player=player).first()
            if (pr):
                pr.delete()
        except Exception as e:
            return JsonResponse({'code': 1, 'message': 'Invalid, or not existing Song ID'})
    elif (action == 'djname'):
        player.iidxnick = v
        player.save()
    elif (action == 'iidxid'):
        player.iidxid = v
        player.save()
    elif (action == 'spclass'):
        player.spclass = int(v)
        player.save()
    elif (action == 'dpclass'):
        player.dpclass = int(v)
        player.save()
    else:
        return JsonResponse({'code': 1, 'message': 'invalid action'})
    return JsonResponse({'code': 0, 'message': 'Done'})
"""
user end
"""

# imgdownload/
@csrf_exempt
def imgdownload(request):
    if request.method != "POST":
        # allow only POST method
        raise PermissionDenied
    filename = request.POST['name']
    pngdata = base64.decodestring(request.POST['base64'])
    print "got request: %s (%d byte)" % (filename, len(pngdata))
    r = HttpResponse(pngdata, content_type="application/octet-stream")
    r['Content-Disposition'] = 'attachment; filename=%s' % filename
    return r

# iidx/imgtl/
@csrf_exempt
def imgtl(request):
    if request.method != "POST":
        # allow only POST method
        raise PermissionDenied

    filename = request.POST['name']
    pngdata = base64.decodestring(request.POST['base64'])
    print "got request: %s (%d byte)" % (request.POST['name'], len(pngdata))

    import requests
    import urllib2
    header = {'X-IMGTL-TOKEN': settings.imgtlkey}
    r = requests.post('https://api.img.tl/upload', data={'desc': '', 'filename': filename}, \
            files={'file': (filename, pngdata, 'application/octet-stream')}, headers=header)
    return HttpResponse(r.text)

# iidx/qpro/<iidxid>/
@csrf_exempt
def qpro(request, iidxid):
    if (iidxid.isdigit() and int(iidxid) == 0):
        with open('static/qpro/noname.png', 'r') as f:
            img_blank = f.read()
        return HttpResponse(img_blank, content_type="image/png")

    import urllib2
    qpro_url = 'http://iidx.me/userdata/copula/%s/qpro.png' % iidxid
    try:
        resp = urllib2.urlopen(qpro_url)
        if (resp.info().maintype == "image"):
            return HttpResponse(resp.read(), content_type="image/png")
    except urllib2.HTTPError as e:
        pass

    # cannot found
    with open('static/qpro/blank.png', 'r') as f:
        img_blank = f.read()
    return HttpResponse(img_blank, content_type="image/png")
