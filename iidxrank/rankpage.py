#-*- coding: utf-8 -*-
import iidx
import models
import time
from datetime import datetime
import json
import copy

def get_ranktable(tablename):
    tablename = tablename.upper()
    try:
        ranktable = models.RankTable.objects.get(tablename=tablename)
    except Exception as e:
        return None
    return ranktable

def get_player_from_request(request):
    if (request.user.is_authenticated()):
        return models.Player.objects.filter(user=request.user).first()
    else:
        return None

def get_player_from_user(user):
    return models.Player.objects.filter(user=user).first()

"""
get songs in ranktable
"""
def get_songs_from_ranktable(table):
    songs = []
    cates = table.rankcategory_set.all()
    for cate in cates:
        for item in cate.rankitem_set.all():
            songs.append(item.song)
    return songs

"""
search all candidate(level & type) songs in ranktable
"""
def search_songs_from_ranktable(ranktable):
    t_type = ranktable.type
    t_level = ranktable.level
    song_query = models.Song.objects
    songs = []
    for song in song_query.filter(songtype__istartswith=t_type, songlevel=t_level).all():
        songs.append(song)
    return songs


"""
generate NOPLAY playrecord from song object
"""
def generate_prdata_from_song(song):
    return {
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
            'notes': 0,
        }
    }


"""
common processor of 'playrecord data'
- add 'rate','rank' to each song
- modify 'diff' to uppercase
"""
def process_prdata(music):
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
        notes = float(music['data']['notes'])
        if (notes == 0):
            music['rate'] = 0
        else:
            music['rate'] = music['score'] / float(music['data']['notes']) / 2 * 100
    # make rank
    music['rank'] = iidx.getrank(music['rate'])


"""
get ranktable metadata
"""
def get_ranktable_metadata(ranktable):
    pageinfo = {
        'title': ranktable.tabletitle,
        'titlehtml': ranktable.getTitleHTML(),
        'tablename': ranktable.tablename,
        'type': ranktable.type,
        'copyright': ranktable.copyright,
        'time': ranktable.time,
    }
    return pageinfo

def get_ranktable_statistic(ranktable):
    tabledata = ranktable['categories']

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
    for category in tabledata:
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
    for category in tabledata:
        for x in category['items']:
            for rank in rankcount:
                rankcount[rank] += (x['rank'] == rank)

    return {
        'rank':rankcount,
        'clear':clearcount,
        'rankratio':[],
        'clearratio':[],
        }


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return time.mktime(o.timetuple())
            #time.mktime(ranktable.time.timetuple())
            #return o.isoformat()
        return json.JSONEncoder.default(self,o)

def serialize_ranktable(ranktable):
    return json.dumps(ranktable, cls=DateTimeEncoder)

"""
get pdata from iidx.me object
- add 'pkid', 'tag' for future processing
"""
def get_pdata_from_iidxme(data, ranktable):
    musicdata = []
    userdata = {}
    tabledata = []

    spclass = data['userdata']['spclass']
    dpclass = data['userdata']['dpclass']
    spclassstr = iidx.getdanstring(spclass)
    dpclassstr = iidx.getdanstring(dpclass)

    userdata['iidxmeid'] = data['userdata']['iidxmeid']
    userdata['djname'] = data['userdata']['djname']
    userdata['iidxid'] = data['userdata']['iidxid'].replace('-', '')
    userdata['spclass'] = spclass
    userdata['dpclass'] = dpclass

    # fill userdata metadata
    userdata['spclassstr'] = spclassstr
    userdata['dpclassstr'] = dpclassstr
    # check is player object db exists
    splevel = '-'
    dplevel = '-'
    try:
        player_obj = models.Player.objects.get(iidxid=userdata['iidxid'])
        splevel = round(player_obj.splevel, 2)
        if (splevel == 0):
            splevel = '-'
        dplevel = round(player_obj.dplevel, 2)
        if (dplevel == 0):
            dplevel = '-'
    except Exception as e:
        pass
    userdata['splevel'] = splevel
    userdata['dplevel'] = dplevel


    for music in data['musicdata']:
        music = copy.copy(music)
        process_prdata(music)
        musicdata.append(music)

        # add song pk/tag
        song_query = models.Song.objects
        try:
            song_obj = song_query.get(songid=music['data']['id'], songtype=music['data']['diff_detail'])
            music['pkid'] = song_obj.id
            music['tags'] = song_obj.get_tags()
        except Exception as e:
            music['pkid'] = -1
            music['tags'] = []

    pdata = {
        'userdata': userdata,
        'categories': categorize_musicdata(musicdata, ranktable),
        'tableinfo': get_ranktable_metadata(ranktable),
        }
    pdata['statistic'] = get_ranktable_statistic(pdata)

    return pdata


"""
get pdata from player object
- if player==None, then return DJ NONAME (empty player)
"""
def get_pdata_from_player(player, ranktable):
    musicdata = []
    userdata = {}
    tabledata = []

    # generate player data
    if (player == None):
        userdata['djname'] = 'NONAME'
        userdata['iidxid'] = '00000000'
        userdata['spclass'] = 1
        userdata['dpclass'] = 1
        userdata['spclassstr'] = iidx.getdanstring(1)
        userdata['dpclassstr'] = iidx.getdanstring(1)

        # generate player records
        songs = get_songs_from_ranktable(ranktable)
        for song in songs:
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
                    'notes': 0,
                },
                'tags': song.get_tags(),
                'score': 0,
            }
            process_prdata(music)
            musicdata.append(music)
    else:
        userdata['djname'] = player.iidxnick
        userdata['iidxid'] = player.iidxid.replace('-','')
        userdata['spclass'] = player.spclass
        userdata['dpclass'] = player.dpclass
        userdata['spclassstr'] = iidx.getdanstring(player.spclass)
        userdata['dpclassstr'] = iidx.getdanstring(player.dpclass)

        # generate player records
        songs = get_songs_from_ranktable(ranktable)
        for song in songs:
            pr = models.PlayRecord.objects.filter(player=player,song=song).first()

            clear = 0
            score = 0
            rate = 0
            notes = song.songnotes
            if (notes == None):
                notes = 0
            if (pr != None):
                clear = pr.playclear
                if (pr.playscore != None):
                    score = pr.playscore
                if (notes > 0):
                    rate = float(score) / notes

            music = {
                'pkid': song.pk,
                'rate': rate,
                'rank': iidx.getrank(rate),
                'clear': clear,
                'clearstring': iidx.getclearstring(clear),
                'data': {
                    'diff_detail': song.songtype,
                    'diff': song.songtype[-1:],
                    'title': song.songtitle,
                    'id': song.songid,
                    'version': song.version,
                    'notes': notes,
                },
                'tags': song.get_tags(),
                'score': score,
            }
            musicdata.append(music)

    pdata = {
        'userdata': userdata,
        'categories': categorize_musicdata(musicdata, ranktable),
        'tableinfo': get_ranktable_metadata(ranktable),
        }
    pdata['statistic'] = get_ranktable_statistic(pdata)
    return pdata

"""
categorize playdata
"""
def categorize_musicdata(musicdata, ranktable, remove_empty_category=True):
    # sort musicdata by name
    def sort_musicdata(x, y):
        x_ = x['data']['title'].upper()
        y_ = y['data']['title'].upper()
        if (x_ > y_):
            return 1
        elif (x_ == y_):
            return 0
        else:
            return -1
    musicdata.sort(sort_musicdata)

    # 
    # make category-processed array
    # - find each song data's category and add to that array
    #
    item_to_category = {}           # key: songitem pkid
    item_itemid = {}
    categories_dict = {}            # key: category pkid
    for category in ranktable.rankcategory_set.all():
        for item in category.rankitem_set.all():
            item_to_category[item.song.id] = category.id
            item_itemid[item.song.id] = item.id
        sortindex = category.get_sortindex()
        if (not sortindex):
            sortindex = 0
        categories_dict[category.id] = {
            'category': category.categoryname,
            'categorytype': category.categorytype,
            'sortindex': sortindex,
            'categoryclearstring': iidx.getclearstring(7),
            'categoryclear': 7,
            'items': [],
        }
    categories_dict[-1] = {
        'category': '-',
        'categorytype': 1,
        'sortindex': -100,
        'categoryclearstring': iidx.getclearstring(7),
        'categoryclear': 7,
        'items': [],
    }
    for music in musicdata:
        pkid = music['pkid']
        if (pkid in item_to_category):
            music['itemid'] = item_itemid[pkid]
            categories_dict[item_to_category[pkid]]['items'].append(music)
        else:
            music['itemid'] = -1
            categories_dict[-1]['items'].append(music)

    # convert dictionary to normal array
    categories = []
    for k, v in categories_dict.iteritems():
        v['id'] = k
        categories.append(v)

    # category lamp process
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

    if (remove_empty_category):
        categories_copy = []
        for category in categories:
            if (len(category['items']) > 0):
                categories_copy.append(category)
    else:
        categories_copy = categories
    return sorted(categories_copy, cmp=sort_func)















# DEPRECIATED PART


"""
merge player data into ranktable
"""
def get_player_data(pobj, ranktable):
    player = {}
    musicdata = []
    player['userdata'] = {}
    player['userdata']['djname'] = pobj.iidxnick
    player['userdata']['spclass'] = pobj.spclass
    player['userdata']['dpclass'] = pobj.dpclass
    player['userdata']['iidxid'] = pobj.iidxid
    player['musicdata'] = musicdata

    songs = get_songs_from_ranktable(ranktable)
    for song in songs:
        pr = models.PlayRecord.objects.filter(player=pobj,song=song).first()

        clear = 0
        score = 0
        rate = 0
        notes = song.songnotes
        if (notes == None):
            notes = 0
        if (pr != None):
            clear = pr.playclear
            if (pr.playscore != None):
                score = pr.playscore
            if (notes > 0):
                rate = float(score) / notes

        music = {
            'pkid': song.pk,
            'rate': rate,
            'rank': iidx.getrank(rate),
            'clear': clear,
            'clearstring': iidx.getclearstring(clear),
            'data': {
                'diff_detail': song.songtype,
                'diff': song.songtype[-1:],
                'title': song.songtitle,
                'id': song.songid,
                'version': song.version,
                'notes': notes,
            },
            'tags': song.get_tags(),
            'score': score,
        }
        musicdata.append(music)

    return player

def compile_data(ranktable, player, song_query, removeEmptyCategory=True):
    # get userinfo first
    userinfo = getUserInfo(player)

    # create score data
    # [(category, [(songname, score, clear ...)])]
    musicdata = None
    if (player is not None):
        musicdata = player['musicdata']
    score = addMetadata(musicdata, ranktable, song_query)
    if (removeEmptyCategory):
        r = []
        for category in score:
            if (len(category['items']) > 0):
                r.append(category)
        score = r

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


"""
# addMetadata: push score data to user's musicdata
#
# dict: category -> songs[] (title, code, clear, ex, ...)
TODO: use get_songs_with_ranktable
"""
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
                    'notes': 0,
                },
                'tags': song.get_tags(),
                'score': 0,
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
                notes = float(music['data']['notes'])
                if (notes == 0):
                        music['rate'] = 0
                else:
                        music['rate'] = music['score'] / float(music['data']['notes']) / 2 * 100
            
            # make rank
            music['rank'] = iidx.getrank(music['rate'])

            # add song pk id
            try:
                song_obj = song_query.get(songid=music['data']['id'], songtype=music['data']['diff_detail'])
                music['pkid'] = song_obj.id
                music['tags'] = song_obj.get_tags()
            except:
                music['pkid'] = -1
                music['tags'] = []

    # sort musicdata by name
    def sort_musicdata(x, y):
        x_ = x['data']['title'].upper()
        y_ = y['data']['title'].upper()
        if (x_ > y_):
            return 1
        elif (x_ == y_):
            return 0
        else:
            return -1
    musicdata.sort(sort_musicdata)

    # 
    # make category-processed array
    # - find each song data's category and add to that array
    #
    item_to_category = {}           # key: songitem pkid
    item_itemid = {}
    categories_dict = {}            # key: category pkid
    for category in data.rankcategory_set.all():
        for item in category.rankitem_set.all():
            item_to_category[item.song.id] = category.id
            item_itemid[item.song.id] = item.id
        sortindex = category.get_sortindex()
        if (not sortindex):
            sortindex = 0
        categories_dict[category.id] = {
            'category': category.categoryname,
            'categorytype': category.categorytype,
            'sortindex': sortindex,
            'categoryclearstring': iidx.getclearstring(7),
            'categoryclear': 7,
            'items': [],
        }
    categories_dict[-1] = {
        'category': '-',
        'categorytype': 1,
        'sortindex': -100,
        'categoryclearstring': iidx.getclearstring(7),
        'categoryclear': 7,
        'items': [],
    }
    for music in musicdata:
        pkid = music['pkid']
        if (pkid in item_to_category):
            music['itemid'] = item_itemid[pkid]
            categories_dict[item_to_category[pkid]]['items'].append(music)
        else:
            music['itemid'] = -1
            categories_dict[-1]['items'].append(music)
    # convert dictionary to normal array
    categories = []
    for k, v in categories_dict.iteritems():
        v['id'] = k
        categories.append(v)

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
