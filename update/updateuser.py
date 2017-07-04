#-*- coding: utf-8 -*-
#
# algorithm from: http://walkure.net/hakkyou/komakai.html#komakaihanashi
#
import math
import parser_iidxme
import time
from datetime import datetime, date
import log
import iidxrank.models as models

# user update part
def add_user(user):
    obj_player = models.Player.objects.filter(iidxid=user[2]).first()
    if (obj_player):
        # edit nickname
        obj_player.iidxnick = user[0]
        obj_player.iidxmeid = user[1]
        obj_player.save()
        return 0
    else:
        # add new user
        obj_player = models.Player.objects.create(iidxid=user[2], 
            iidxnick=user[0],
            iidxmeid=user[1],
            time=datetime.min,
            sppoint=0,
            dppoint=0,
            spclass=0,
            dpclass=0,
            splevel=0,
            dplevel=0)
        return 1

def update_user():
    add_count = 0
    for user in parser_iidxme.parse_users():
        add_count += add_user(user)
    log.Print('added %d users' % add_count)

# user update part end





# user playrecord update part
def update_user_from_data(player, user_info):
    add_count = 0
    # add clear data
    for playrecord in user_info['musicdata']:
        if (playrecord['clear'] >= 1):  # over failed user
            song = models.Song.objects.filter(songid=playrecord['data']['id'], songtype=playrecord['data']['diff'].upper())
            if (not song.count()):
                continue
            else:
                song = song.first()
            playrecord_objects = models.PlayRecord.objects.filter(player_id=player.id, song_id=song.id).first()
            if (playrecord_objects):
                # just update clear
                pr = playrecord_objects
                if (playrecord['score']):
                    pr.playscore = playrecord['score']
                if (playrecord['miss']):
                    pr.playmiss = playrecord['miss']
                pr.playclear = playrecord['clear']
            else:
                # add new one
                models.PlayRecord.objects.create(playscore=playrecord['score'],
                    playclear=playrecord['clear'],
                    playmiss=playrecord['miss'],
                    player_id=player.id,
                    song_id=song.id)
                add_count += 1

    return add_count

def update_playrecord_obj(player):
    add_count = 0
    sppoint = 0
    dppoint = 0
    spclass = 0
    dpclass = 0
    # start from level 8
    for mode in ("sp", "dp"):
        for i in range(8, 13):
            try:
                log.Print('updating user %s (%s) - (%s, %d) ...' % (player.iidxmeid, player.iidxnick, mode, i))
                user_info = parser_iidxme.parse_user(player.iidxmeid, mode, i)
                sppoint = user_info['userdata']['sppoint']
                dppoint = user_info['userdata']['dppoint']
                spclass = user_info['userdata']['spclass']
                dpclass = user_info['userdata']['dpclass']
                add_count += update_user_from_data(player, user_info)
                time.sleep(0.1)     # to avoid being suspend as traffic abusing
            except (KeyboardInterrupt, SystemExit):
                log.Print('bye')
                exit()
            except:
                log.Print('error during parsing. ignore error and continue')
    player.sppoint = sppoint
    player.dppoint = dppoint
    player.spclass = spclass
    player.dpclass = dpclass
    player.time = datetime.utcnow()

    return add_count

# --- http begin ---

def update_user_from_data_http(player, user_info):
    add_count = 0
    # add clear data
    for playrecord in user_info['musicdata']:
        if (playrecord['clear'] >= 1):  # over failed user
            song = models.Song.objects.filter(songid=playrecord['data']['id'], songtype=playrecord['data']['diff'].upper())
            if (not song.count()):
                continue
            else:
                song = song.one()
            playrecord_objects = models.PlayRecord.objects.filter(player_id=player.id, song_id=song.id).first()
            if (playrecord_objects):
                # just update clear
                pr = playrecord_objects.one()
                if (playrecord['score']):
                    pr.playscore = playrecord['score']
                if (playrecord['miss']):
                    pr.playmiss = playrecord['miss']
                pr.playclear = playrecord['clear']
            else:
                # add new one
                models.PlayRecord.objects.create(playscore=playrecord['score'],
                    playclear=playrecord['clear'],
                    playmiss=playrecord['miss'],
                    player_id=player.id,
                    song_id=song.id)
                add_count += 1

    return add_count

def update_playrecord_obj_http(player):
    if (player.iidxmeid.startswith('user_')):
        print 'No iidx.me user, skip %s' % player.iidxmeid
        return 0
    add_count = 0
    sppoint = 0
    dppoint = 0
    spclass = 0
    dpclass = 0
    # start from level 8
    #for mode in ("sp", "dp"):
    #    for i in range(10, 13):
    if (player.spclass >= 16):
        return
    for mode in ("sp",):
        for i in range(8, 10):
            try:
                log.Print('updating user %s (%s) - (%s, %d) ...' % (player.iidxmeid, player.iidxnick, mode, i))
                user_info = parser_iidxme.parse_user_http(player.iidxmeid, mode, i)
                sppoint = 0 #user_info['userdata']['sppoint']
                dppoint = 0 #user_info['userdata']['dppoint']
                spclass = user_info['userdata']['spclass']
                dpclass = user_info['userdata']['dpclass']
                add_count += update_user_from_data(player, user_info)
                time.sleep(0.1)     # to avoid being suspend as traffic abusing
            except (KeyboardInterrupt, SystemExit):
                log.Print('bye')
                exit()
            except Exception as e:
                print e
                log.Print('error during parsing. ignore error and continue')
    player.sppoint = sppoint
    player.dppoint = dppoint
    player.spclass = spclass
    player.dpclass = dpclass
    player.time = datetime.utcnow()

    return add_count

# --- http end ---

def update_playrecord(iidxmeid):
    obj_player = models.Player.objects.filter(iidxmeid=iidxmeid).first()
    if (obj_player == None):
        # TODO: create user, in case of this.
        return False
    update_playrecord_obj_http(obj_player)
    return True

def update_playrecord_all():
    for obj_player in models.Player.objects.all():
        update_playrecord_obj_http(obj_player)
# user playrecord update part end


