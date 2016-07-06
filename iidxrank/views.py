#-*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import render, render_to_response
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.clickjacking import xframe_options_exempt
from django.core.paginator import Paginator
import models
import settings

from update import jsondata
import rankpage as rp
import iidx
import json

import base64

def checkValidPlayer(player):
  return not (player == None or 
    'userdata' not in player or 
    player['status'] != 'success')

####

def mainpage(request):
  notices = models.Board.objects.filter(title='notice').first().boardcomment_set
  return render_to_response('notice.html', {'notices': notices.order_by('-time')})

def userpage(request, username="!"):
  if (username == "!"):
    # make dummy data
    player = {
      'userdata': {
        'djname': 'NONAME',
        'iidxid': '0',
        'spclass': 0,
        'dpclass': 0,
      }
    }
  else:
    # check recent json to get player info
    userjson_url = "http://json.iidx.me/%s/recent/" % username
    player = jsondata.loadJSONurl(userjson_url)
    if (not checkValidPlayer(player)):
      # invalid user!
      raise Http404

    # check is db exists
    try:
      player_obj = models.Player.objects.get(iidxid=player['userdata']['iidxid'])
      splevel = round(player_obj.splevel, 2)
      if (splevel == 0):
        splevel = '-'
      dplevel = round(player_obj.dplevel, 2)
      if (dplevel == 0):
        dplevel = '-'
    except:
      splevel = '-'
      dplevel = '-'
  
  playerinfo = {
    'userid': username,
    'username': player['userdata']['djname'],
    'iidxid': player['userdata']['iidxid'].replace('-', ''),
    'spclass': iidx.getdanstring(player['userdata']['spclass']),
    'dpclass': iidx.getdanstring(player['userdata']['dpclass']),
    'splevel': splevel, # estimated level
    'dplevel': dplevel, # estimated level
  }

  # TODO: apart userpage from index. change index to search.
  return render_to_response('userpage.html', {'userinfo': playerinfo})

def rankpage(request, username="!", diff="SP", level=12):
  # check is argument valid
  diff = diff.upper()
  level = level.upper()
  try:
    ranktable = models.RankTable.objects.get(tablename=diff+level)
  except:
    # invalid table!
    raise Http404

  # load player json data
  if (username == "!"):
    player = None
  else:
    userjson_url = "http://json.iidx.me/%s/%s/level/%d/" % (username, ranktable.type.lower(), ranktable.level)
    player = jsondata.loadJSONurl(userjson_url)
    if (not checkValidPlayer(player)):
      # invalid user!
      raise Http404
  
  # compile user data to render score
  userinfo, songdata, pageinfo = rp.compile_data(ranktable, player, models.Song.objects)
  userinfo['title'] = pageinfo['title']
  tabledata = {
      'info': userinfo,
      'categories': songdata
      }
  return render_to_response('rankview.html', 
      {'score': songdata, 
        'tabledata_json': json.dumps(tabledata),
        'userinfo': userinfo, 
        'pageinfo': pageinfo}
      )

def songcomment_all(request, page=1):
  songcomment_list = models.SongComment.objects.order_by('-time').all()
  paginator = Paginator(songcomment_list, 100)
  
  try:
    songcomments = paginator.page(page)
  except:
    # invalid pagenation!
    raise Http404

  return render_to_response('songcomment_all.html', {"comments": songcomments})


# /iidx/musiclist
#@xframe_options_exempt
def musiclist(request):
  # all the other things will done in json & html
  return render_to_response('musiclist.html')

# /iidx/(username)/recommend/
def recommend(request, username):
  return render_to_response('recommend.html', {"username": username})

# /iidx/(username)/skillrank
def skillrank(request, username):
  return render_to_response('skillrank.html', {"username": username})

# /iidx/!/songrank/
def songrank(request):
  return render_to_response('songrank.html')

# /iidx/!/userrank/
def userrank(request):
  return render_to_response('userrank.html')


# iidx/imgtl/
@csrf_exempt
def imgtl(request):
  if request.method != "POST":
    # allow only POST method
    raise PermissionDenied

  filename = request.POST['name']
  pngdata = base64.decodestring(request.POST['base64'])
  print "got imgtl request: %s (%d byte)" % (request.POST['name'], len(pngdata))

  import requests
  import urllib2
  header = {'X-IMGTL-TOKEN': settings.imgtlkey}
  r = requests.post('https://api.img.tl/upload', data={'desc': '', 'filename': filename}, \
    files={'file': (filename, pngdata, 'application/octet-stream')}, headers=header)
  return HttpResponse(r.text)

# iidx/qpro/<iidxid>/
@csrf_exempt
def qpro(request, iidxid):
  import urllib2
  qpro_url = 'http://iidx.me/userdata/copula/%s/qpro.png' % iidxid
  resp = urllib2.urlopen(qpro_url)
  if resp.info().maintype == "image":
    return HttpResponse(resp.read(), content_type="image/png")
  else:
    # cannot found
    f = open('iidxrank/static/qpro/blank.png', 'r')
    img_blank = f.read()
    f.close()
    return HttpResponse(img_blank)
