#-*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.core.exceptions import PermissionDenied
from django.core.exceptions import MultipleObjectsReturned
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
import update.parser_csv as parser_csv
import iidx
import json
import views_json
import base64

import update.parser_iidxme as iidxme


"""
check is iidxme data is valid player data
TODO: make this code in parser_iidxme module
"""
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
        # load player information from DB
        pobj = rp.get_player_from_request(request)
        userinfo = rp.get_udata_from_player(pobj)
    else:
        # check recent json to get player info
        #userjson_url = "http://json.iidx.me/%s/recent/" % username
        #player = jsondata.loadJSONurl(userjson_url)
        userpage_url = "http://iidx.me/%s/recent/" % username
        player = iidxme.parse_iidxme_http(userpage_url)
        if (not checkValidPlayer(player)):
            # invalid user!
            raise Http404
        userinfo = rp.get_udata_from_iidxme(player)
    return render(request, 'user/userpage.html', {'userdata': userinfo})

def get_pdata(request,username,tablename):
    table = rp.get_ranktable(tablename)
    if (table == None):
        #raise Http404
        return None
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
            #raise Http404
            return None
        pdata = rp.get_pdata_from_iidxme(iidxme_data,table)
    # only session authorized user can edit table.
    if (player):
        pdata['editable']=True
    else:
        pdata['editable']=False
    return pdata

def rankpage(request, username="!", tablename="SP12"):
    pdata = get_pdata(request,username,tablename)
    if (pdata == None):
        raise Http404
    # append additional data
    pdata['tabledata_json'] = rp.serialize_ranktable(pdata)
    return render(request, 'user/rankview.html', pdata)

"""
def detailpage(request, username="!", tablename="SP12"):
    d = retrieve_userdata(username, tablename)
    return render(request, 'user/detailview.html', d)
"""

def ranktable(request, username="!", tablename="SP12"):
    pdata = get_pdata(request,username,tablename)
    if (pdata == None):
        raise Http404
    if (request.GET.get('edit') != None):
        pdata['edit'] = True
    return render(request, 'ranktable.html', pdata)

def rankjson(request, username="!", tablename="SP12"):
    pdata = get_pdata(request,username,tablename)
    if (pdata == None):
        raise Http404
    return JsonResponse(pdata)

def rankedit(request, id=-1):
    # render rankedit page for each user (for internal load)
    if (not request.user.is_authenticated()):
        islogined = False
        valid = False
        pr_obj = None
        title = ''
    else:
        islogined = True
        user = request.user
        # check song is exists
        song_obj = models.Song.objects.filter(id=id).first()
        title = song_obj.songtitle
        if (song_obj == None):
            valid = False
        else:
            valid = True
            # fetch playrecord if available
            pr_obj = models.PlayRecord.objects.filter(player_id=user.id, song_id=id).first()
            if (pr_obj == None):
                pr_obj = models.PlayRecord()
    return render(request, 'user/rankedit.html', {
        'valid': valid,
        'islogined': islogined,
        'title': title,
        'item': pr_obj,
        })

def ranktableedit(request, tablename):
    tablename = tablename.upper()

    # only admin can access it
    if (not request.user.is_staff):
        raise PermissionDenied
    
    # in case of POST? -> return JSON result
    if (request.method == "POST"):
        return views_json.json_rankedit(request)
    
    # check is valid table
    ranktable = models.RankTable.objects.filter(tablename=tablename).first()
    if (ranktable == None):
        raise Http404
    # compile table data
    songs = rp.search_songs_from_ranktable(ranktable)
    prs = rp.generate_pr(songs)
    categories = rp.categorize_musicdata(prs, ranktable, False)
    tableinfo = rp.get_ranktable_metadata(ranktable)
    return render(request, 'rankedit.html', { 'categories': categories, 'tableid': ranktable.id, 'tableinfo': tableinfo })

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
                    first_name=form.data['id'],
                    email=form.data['email'],
                    password=form.data['password'])
            # automatically create player object
            rp.get_player_from_user(user)
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

# /!/account/
def account(request):
    if (not request.user.is_authenticated()):
        return redirect('main')
    user = request.user
    player = rp.get_player_from_request(request)
    if (request.method == "POST"):
        form = forms.AccountForm(request.POST)
        if (form.is_valid()):
            user.first_name = form.data['first_name']
            player.iidxid = form.data['iidxid']
            player.iidxnick = form.data['iidxnick']
            player.spclass = form.data['spclass']
            player.dpclass = form.data['dpclass']
            user.save()
            player.save()
            return redirect('main')
    else:
        form = forms.AccountForm(initial={
            'first_name': user.first_name,
            'iidxid': player.iidxid,
            'iidxnick': player.iidxnick,
            'spclass': player.spclass,
            'dpclass': player.dpclass
            })
    return render(request, 'user/account.html', {'form': form})

# /!/set_password/
def set_password(request):
    if (not request.user.is_authenticated()):
        return redirect('main')
    if (request.method == "POST"):
        form = forms.SetPasswordForm(request.POST)
        if (form.is_valid()):
            user = request.user
            user.set_password(form.data['new_password'])
            user.save()
            return redirect('main')
    else:
        form = forms.SetPasswordForm()
    return render(request, 'user/setpassword.html', {'form':form})

# /!/update/
# XXX: should allow cross-domain request to allow extern site
@csrf_exempt
def updatelamp(request):
    form = {'is_valid': True, 'errors':'no errors.', 'message': ['Ready.',]}
    if (request.method == "POST"):
        if (not request.user.is_authenticated()):
            return JsonResponse({'status': 'Please login to iidx.me first.'})
        if ('type' not in request.POST or 'file' not in request.FILES):
            form['is_valid'] = False
            form['errors'] = 'Invalid form data.'
        else:
            import csv
            csvtype = request.POST['type']
            csvfile = request.FILES['file']
            tbl = csv.reader(csvfile, delimiter=',')
            log = []
            print "* updatelamp: user %s, %s" % (request.user.username, csvtype)
            parser_csv.update(tbl, csvtype, request.user, log)
            form['message'] = log
            print "* updatelamp end."
    if (not request.user.is_authenticated()):
        return redirect('main')
    return render(request, 'user/updatelamp.html', {'form':form})

# JSON
# /!/modify/
def modify(request):
    if (not request.user.is_authenticated()):
        return JsonResponse({'code': 1, 'message': 'please log in'})
    user = request.user
    player = rp.get_player_from_request(request)
    if (request.method == "POST"):
        action = request.POST.get('action', '')
        v = request.POST.get('v', '')
    else:
        action = request.GET.get('action', '')
        v = request.GET.get('v', '')
    if (action == 'edit'):
        lst = json.loads(v)
        for l in lst:
            sid = int(l['id'])
            desc = { 'clear': int(l['clear']) }
            if ('rate' in l):
                desc['rate'] = float(l['rate'])
            if ('rank' in l):
                desc['rank'] = l['rank']
            if ('score' in l):
                desc['score'] = int(l['score'])
            log = []
            if (not rp.update_record(sid, player, desc, log)):
                return JsonResponse({
                    'code': 1,
                    'message': log[0],
                    'detail':str(e)
                })
    elif (action == 'delete'):
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
def qpro(request, iidxid='!'):
    if ((iidxid.isdigit() and int(iidxid) == 0) or iidxid=='!' ):
        with open('static/qpro/noname.png', 'r') as f:
            img_blank = f.read()
        return HttpResponse(img_blank, content_type="image/png")

    import urllib2
    #qpro_url = 'http://iidx.me/userdata/copula/%s/qpro.png' % iidxid
    qpro_url = iidxme.parse_qpro(iidxid)
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
