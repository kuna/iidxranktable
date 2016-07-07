#-*- coding: utf-8 -*-
import iidx
import models
import time

def compile_data(ranktable, player, song_query):
  # get userinfo first
  userinfo = getUserInfo(player)

  # create score data
  # [(category, [(songname, score, clear ...)])]
  musicdata = None
  if (player is not None):
    musicdata = player['musicdata']
  score = addMetadata(musicdata, ranktable, song_query)

  # count clear counts
  clearcount = {
    'noplay': 0,
    'failed': 0,
    'assist': 0,
    'easy': 0,
    'normal': 0,
    'hard': 0,
    'exhard': 0,
    'fullcombo': 0
  }
  for category in score:
    for x in category['items']:
      clearcount['noplay'] += (x['clear'] == 0)
      clearcount['failed'] += (x['clear'] == 1)
      clearcount['assist'] += (x['clear'] == 2)
      clearcount['easy'] += (x['clear'] == 3)
      clearcount['normal'] += (x['clear'] == 4)
      clearcount['hard'] += (x['clear'] == 5)
      clearcount['exhard'] += (x['clear'] == 6)
      clearcount['fullcombo'] += (x['clear'] == 7)

  # count rank
  rankcount = {
    'AAA': 0,
    'AA': 0,
    'A': 0,
    'B': 0,
    'C': 0,
    'D': 0,
    'E': 0,
    'F': 0,
  }
  for category in score:
    for x in category['items']:
      for rank in rankcount:
        rankcount[rank] += (x['rank'] == rank)

  # make information for page/table
  pageinfo = {
    'title': ranktable.tabletitle,
    'titlehtml': ranktable.getTitleHTML(),
    'tablename': ranktable.tablename,
    'type': ranktable.type,
    'clearinfo': clearcount,
    'rankinfo': rankcount,
    'copyright': ranktable.copyright,
    'date': ranktable.time,
  }
  userinfo['tabletime'] = time.mktime(ranktable.time.timetuple())
  userinfo['copyright'] = ranktable.copyright
  return userinfo, score, pageinfo


#
# addMetadata: push score data to user's musicdata
#
# dict: category -> songs[] (title, code, clear, ex, ...)
def addMetadata(musicdata, data, song_query):
  #
  # preprocess musicdata
  # - add 'rate', 'rank' to each song
  #
  if (musicdata == None):
    musicdata = []
    for song in song_query.filter(songtype__istartswith=data.type, songlevel=data.level).all():
      music = {
        'pkid': song.pk,
        'rate': 0,
        'rank': iidx.getrank(0),
        'clear': 0,
        'clearstring': iidx.getclearstring(0),
        'data': {
          'diff_detail': song.songtype,
          'diff': song.songtype[-1:],
          'title': song.songtitle,
          'id': song.songid,
          'version': song.version,
        },
      }
      musicdata.append(music)
  else:
    for music in musicdata:
      # make diff(DP + A) string upper
      music['data']['diff_detail'] = music['data']['diff']
      music['data']['diff'] = music['data']['diff'][-1:].upper()

      # add clear metadata (number to readable string)
      clear = int(music['clear'])
      music['clearstring'] = iidx.getclearstring(clear)

      # make rate (sometimes note data isn't provided -> 0)
      if (music['score'] == None or music['data']['notes'] == None):
        music['rate'] = 0
      else:
        music['rate'] = music['score'] / float(music['data']['notes']) / 2 * 100
      
      # make rank
      music['rank'] = iidx.getrank(music['rate'])

      # add song pk id
      try:
        song_obj = song_query.get(songid=music['data']['id'], songtype=music['data']['diff_detail'])
        music['pkid'] = song_obj.id
      except:
        music['pkid'] = -1

  # 
  # make processed array
  # - find each song data's category and add to that array
  #
  categories = []       # processed category datas
  categories_prefetch = []  # prefetched category datas from DB
  for category in data.rankcategory_set.all():
    items = []
    for item in category.rankitem_set.all():
      items.append(item)
    categories_prefetch.append({
      'category': category, 
      'items': items,
    })
  def getCategoryProcessed(category_model=None):
    # none model means, '-'(no category)
    if (category_model == None):
      categoryname = '-'
      categorytype = 1      # big category
      sortindex = 0
    else:
      categoryname = category_model.categoryname
      categorytype = category_model.categorytype
      sortindex = category_model.get_sortindex()
      if (not sortindex):
        sortindex = 0
    # if processed category exists, then return it
    for category in categories:
      if (category['category'] == categoryname):
        return category
    # if category is not exist, then make new one
    category = { 'category': categoryname, 
        'items': [],
        'sortindex': sortindex,
        'categorytype': categorytype,
        'categoryclearstring': u'FULL_COMBO',
        'categoryclear': 7 }  # default setting
    categories.append(category)
    return category
  def getCategoryDB(songpkid):
    for category in categories_prefetch:
      for item in category['items']:
        # ASSERT! some deleted song may have no 'song relation item'
        # ASSERT! item's difficulty(type) must considered)
        if (item.song \
          and item.song.id == int(songpkid)):
          return category['category']
    return None   # cannot find category

  for music in musicdata:
    category = getCategoryDB(music['pkid'])
    if (category == None):
      getCategoryProcessed()['items'].append(music)
    else:
      getCategoryProcessed(category)['items'].append(music)

  #
  # category lamp process
  #
  for catearray in categories:
    for song in catearray['items']:
      if (song['clear'] < catearray['categoryclear']):
        catearray['categoryclear'] = song['clear']
        catearray['categoryclearstring'] = song['clearstring']

  # process category sorting (big value is first one)
  def sort_func(x, y):
    def getValue(_x):
      return _x['sortindex']
    # bigger: later
    return int((getValue(y) - getValue(x))*1000)
  return sorted(categories, cmp=sort_func)

#
# just get user info from json data
#
def getUserInfo(player, iidxmeid=''):
  # if player is none, then all the information will be set null
  if (player == None):
    player = {}
    player['musicdata'] = None
    player['userdata'] = {}
    player['userdata']['djname'] = 'NONAME'
    player['userdata']['spclass'] = 1
    player['userdata']['dpclass'] = 1
    player['userdata']['iidxid'] = '00000000'

  # check is db exists
  try:
    player_obj = models.Player.objects.get(iidxid=player['userdata']['iidxid'])
    splevel = round(player_obj.splevel, 2)
    if (splevel == 0):
      splevel = '-'
    dplevel = round(player_obj.dplevel, 2)
    if (dplevel == 0):
      dplevel = '-'
  except Exception as e:
    #print e
    splevel = '-'
    dplevel = '-'

  spclass = player['userdata']['spclass']
  dpclass = player['userdata']['dpclass']
  spclassstr = iidx.getdanstring(spclass)
  dpclassstr = iidx.getdanstring(dpclass)

  userinfo = {
      'iidxmeid': iidxmeid,
      'username': player['userdata']['djname'],
      'iidxid': player['userdata']['iidxid'].replace('-', ''),
      'spclass': player['userdata']['spclass'],
      'dpclass': player['userdata']['dpclass'],
      'spclassstr': spclassstr,
      'dpclassstr': dpclassstr,
      'splevel': splevel, # estimated level
      'dplevel': dplevel, # estimated level
      }
  return userinfo
