#-*- coding: utf-8 -*-
#
# using MCMC algorithm

import math
from random import random as rand
import random
import log
import models as m
import iidxrank.models as models

# basic initalization
diffs = ['easy', 'normal', 'hd', 'exh']
diffs_num = {'easy':3, 'normal':4, 'hd':5, 'exh':6}

# make score per clear status
# (used for player)
def clearScore(playclear, type=None):
    if (type == None):
        if (playclear == 1):
            return 0
        elif (playclear == 2):
            return 0
        elif (playclear == 3):
            return 0.3
        elif (playclear == 4):
            return 0.4
        elif (playclear == 5):
            return 0.7
        elif (playclear == 6):
            return 0.9
        elif (playclear == 7):
            return 1

    def getScoreValue(clear_goal):
        if (playclear < clear_goal):
            return 0
        else:
            return 1
    if (type in diffs_num):
        return getScoreValue(diffs_num[type])
    else:
        raise Exception("unsupported type of difficulty")

# common functions
def norm(x, std):
    return 1/(math.sqrt(
        2*math.pi)*std)*math.exp(
        -(x-0)**2/(2*std**2))

def rnorm(std):
    return norm(rand()*10, std)

def randomTest(p):
    return p<=rand()

def sigmoid(a, b, x):
    cst = -b*(x-a)
    if (cst > 30):
        return 0
    elif (cst < -30):
        return 1
    else:
        return 1/(1+math.exp(cst))

def sigmoid_error(a,b,lx,ly):
    cul = 0
    for x,y in zip(lx,ly):
        # mainly: x is level, y is clear/stat et al...
        # model is inversed in song!
        cul += (y - sigmoid(a,b,x))**2
    return cul

iterate_time = 5
b_delta = 1
def sigmoid_regression(a,b,lx,ly):
    # check is it too far away;
    # that is, over range of biggest or smallest one?
    if (a > max(lx) or a < min(lx)):
        a = None
    # if basic a value isn't exists
    # then set it as average of a
    if (a == None):
        a = reduce(lambda x,y: x+y, lx) / len(lx)
    # where to go; up or down?
    delta = 1
    #if (sigmoid_error(a-0.5,b,lx,ly) < sigmoid_error(a+0.5,b,lx,ly)):
    #    delta = -1
    # MCMC to calculate a & b
    error = sigmoid_error(a,b,lx,ly)
    oa = a
    ob = b
    for t in range(iterate_time):
        na = random.uniform(oa-delta/2.0,oa+delta/2.0)
        ne = sigmoid_error(na,b,lx,ly)
        if (ne < error):
            a = na
            error = ne
    for t in range(iterate_time):
        nb = random.uniform(ob-b_delta/2.0,ob+b_delta/2.0)
        if (nb*b <= 0):     # negativity totally changes function - we should avoid it
            continue
        ne = sigmoid_error(a,nb,lx,ly)
        if (ne < error):
            b = nb
            error = ne
    return a,b

# reject if player has 
# - no playrecord / no fail / only fullcombo
# - playrecord under 50
# - ee
def checkValidPlayer(player):
    if (len(player.playrecord) == 0):
        return False
    return True

# reject if song has
# - no user played
def checkIsValidSong(song):
    if (len(song.player) == 0):
        return False
    return True

# common functions end





# user calculation
def prepare_user_obj(obj_player):
    if (not hasattr(obj_player, 'playercalc')):
        tag = '%s %d/%d' % (obj_player.iidxmeid, obj_player.spclass, obj_player.dpclass)
        tag = tag[:20]
        obj = m.PlayerCalc.objects.create(
            player=obj_player,
            tag=tag,
            valid=0,
            sp_l=0,
            sp_w=1,
            dp_l=0,
            dp_w=1
            )
    else:
        obj = obj_player.playercalc

    # check is user score is calculatable
    """
    sp_cnt = 0
    dp_cnt = 0
    for pr in obj_player.playrecord_set.all():
        songtype = pr.song.songtype[:2].upper()
        if songtype == "SP":
            sp_cnt += 1
        elif songtype == "DP":
            dp_cnt += 1
    if (sp_cnt < 30):
        obj.sp_w = 0
    if (dp_cnt < 30):
        obj.dp_w = 0
        """

def prepare_user_all():
    for obj_player in models.Player.objects.all():
        prepare_user_obj(obj_player)

def get_skill_songs(user):
    sp_plays = []
    dp_plays = []
    for pr in user.playrecord_set.filter(song__songtype__istartswith="SP").order_by('-song__songlevel')[:200]:
        sp_plays.append(pr)
    for pr in user.playrecord_set.filter(song__songtype__istartswith="DP").order_by('-song__songlevel')[:200]:
        dp_plays.append(pr)
        """
        songtype = pr.song.songtype[:2].upper()
        if (songtype == "SP"):
        elif (songtype == "DP"):
            dp_plays.append(pr)
            """
    sp_plays.sort(key=lambda obj: obj.getScoreCalculated, reverse=True)
    dp_plays.sort(key=lambda obj: obj.getScoreCalculated, reverse=True)
    return sp_plays, dp_plays

def calculate_user_obj(user):
    # if you don't have failed - we don't care!
    # this modeling - get score for top 20 songs (so must prepare/calc song score first)
    # and average it to make user's.
    sp_songs, dp_songs = get_skill_songs(user)
    print '%d, cnt: %d/%d' % (user.id, len(sp_songs), len(dp_songs))
    # check is user score is calculatable
    if (len(sp_songs) > 20):
        sp_score = 0
        for i in range(20):
            sp_score += sp_songs[i].getScoreCalculated
        user.playercalc.sp_l = sp_score / 20.0
        user.playercalc.sp_w = 1
    else:
        user.playercalc.sp_w = 0
    if (len(dp_songs) > 20):
        dp_score = 0
        for i in range(20):
            dp_score += dp_songs[i].getScoreCalculated
        user.playercalc.dp_l = dp_score / 20.0
        user.playercalc.dp_w = 1
    else:
        user.playercalc.dp_w = 0
    user.playercalc.save()


def calculate_user_id(iidxmeid):
    obj_player = models.Player.objects.filter(iidxmeid=iidxmeid).first()
    if (obj_player == None):
        return False
    else:
        prepare_user_obj(obj_player)
        calculate_user_obj(obj_player)
        return True

def calculate_user_all():
    for obj_player in models.Player.objects.all():
        calculate_user_obj(obj_player)
# user calculation end





# song calculation
def calculate_song_obj(obj):
    if (not obj.valid):
        return
    lx = []
    ly = []
    song = obj.song
    songtype = song.songtype[:2].upper()
    for pr in song.playrecord_set.all():
        if songtype == "SP":
            if (pr.player.playercalc.sp_w > 0):
                lx.append(pr.player.playercalc.sp_l)
                ly.append(pr.playclear)
        elif songtype == "DP":
            if (pr.player.playercalc.dp_w > 0):
                lx.append(pr.player.playercalc.dp_l)
                ly.append(pr.playclear)

    print '-- info --'
    print 'songlevel: %d' % song.songlevel

    # easy, hard, ex
    obj.ez_w = 1
    obj.nm_w = 1
    obj.hd_w = 1
    obj.ex_w = 1
    if (obj.valid < 3):
        lyy = [0 if y<3 else 1 for y in ly]
        ez_l, ez_w = sigmoid_regression(obj.ez_l,obj.ez_w,lx,lyy)
        obj.ez_l = ez_l
        obj.ez_w = ez_w
    if (obj.valid < 4):
        lyy = [0 if y<4 else 1 for y in ly]
        nm_l, nm_w = sigmoid_regression(obj.nm_l,obj.nm_w,lx,lyy)
        obj.nm_l = nm_l
        obj.nm_w = nm_w
    if (obj.valid < 5):
        lyy = [0 if y<5 else 1 for y in ly]
        hd_l, hd_w = sigmoid_regression(obj.hd_l,obj.hd_w,lx,lyy)
        obj.hd_l = hd_l
        obj.hd_w = hd_w

        hd_ly = []
        hd_ln = []
        for x,y in zip(lx,lyy):
            if (y == 0):
                hd_ln.append(x)
            else:
                hd_ly.append(x)
        hd_ly.sort()
        hd_ln.sort()
        print zip(lx,lyy)
        print 'hard not cleared? %d ~ %d (%d)' % (hd_ln[0], hd_ln[-1], len(hd_ln))
        print 'hard cleared?: %d ~ %d (%d)' % (hd_ly[0], hd_ly[-1], len(hd_ly))
    if (obj.valid < 6):
        lyy = [0 if y<6 else 1 for y in ly]
        ex_l, ex_w = sigmoid_regression(obj.ex_l,obj.ex_w,lx,lyy)
        obj.ex_l = ex_l
        obj.ex_w = ex_w
    #print zip(lx,ly)
    print 'hard level: %d' % obj.hd_l
    obj.save()

def calculate_song_all():
    for obj in m.SongCalc.objects.all():
        calculate_song_obj(obj)

def prepare_song_all():
    for obj_song in models.Song.objects.all():
        # if no songcalc exists?
        # then make it
        if (not hasattr(obj_song, 'songcalc')):
            song = obj_song
            tag = '%s%d - %s' % (obj_song.songtype, obj_song.songlevel, obj_song.songtitle[:12])
            obj = m.SongCalc.objects.create(
                song=song,
                tag=tag,
                valid=0,
                ez_l=song.songlevel,
                ez_w=1,
                nm_l=song.songlevel,
                nm_w=1,
                hd_l=song.songlevel,
                hd_w=1,
                ex_l=song.songlevel,
                ex_w=1
                )
        else:
            obj = obj_song.songcalc

        # check validation of song
        # - if no failed user, then cannot calculate - valid=0
        # - if no easy user, then cannot calculate easy - valid=1
        # ...
        valid = 99
        for pr in obj_song.playrecord_set.all():
            if (pr.playclear < valid):
                valid = pr.playclear
                obj.valid = valid
        # in case of arg clear???
        obj.ez_l = obj_song.songlevel-1
        obj.nm_l = obj_song.songlevel-0.5
        obj.hd_l = obj_song.songlevel
        obj.ex_l = obj_song.songlevel+1
        obj.ez_w = 1
        obj.nm_w = 1
        obj.hd_w = 1
        obj.ex_w = 1
        obj.save()
# song calculation end









"""
# graph renderer (requires matplotlib)
def showSongStat(type="SP", onlysave=True, fname="songstat.png"):
    import matplotlib.pyplot as plot        # only for debugee
    if (len(type) != 2):
        raise Exception("invalid song type")

    x = []
    y = []
    for song in db.Song.query.all():
        if (song.songtype[:2] == "SP"):
            x.append(song.songlevel)
            y.append(song.calclevel)
    plot.scatter(x, y, c='r')
    if (onlysave):
        plot.savefig(fname)
    else:
        plot.show()
    plot.clf()

def showPlayerStat(onlysave=True, fname="playerstat.png"):
    import matplotlib.pyplot as plot        # only for debugee
    x = []
    y = []
    for player in db.Player.query.all():
        x.append(player.spclass)
        y.append(player.splevel)
    plot.scatter(x, y, c='r')
    if (onlysave):
        plot.savefig(fname)
    else:
        plot.show()
    plot.clf()
# graph renderer end
# using model (from walkure)
def model_user(a, b, x):
    return 1/(1+math.exp(-a*(x-b)))
def model_song(a, b, x):
    return 1/(1+math.exp(a*(x-b)))

############################################################
# update every user/song level
# using MCMC algorithm
def iterate_song(_range=(-0.5, 0.5), iterate_time=5, diff="hd"):
    calclevel_diff = "calclevel_" + diff
    calcweight_diff = "calcweight_" + diff

    # get clearrate of users whose level is enough
    def getScore(song, level, weight):
        cul = 0
        for precord in song.playrecord:
            if (precord.playclear == 0):    # ignore noclear
                continue
            v = clearScore(precord.playclear, diff)
            player_level = 0
            if (song.songtype[:2] == "SP"):
                player_level = precord.player.splevel
            else:
                player_level = precord.player.dplevel
            # ignore too much low or high score
            if (player_level >2 or player_level < 18):
                continue
            # get models' clear estimation of suggested 'level'
            cul += (v - model_song(weight, player_level, level))**2 # model is inversed in song!
        return cul

    i = 0
    songs = db_session.query(db.Song).all()
    error_sum = 0
    for song in songs:
        if (i%10==0):
            log.Print("%d/%d" % (i, len(songs)))
        i+=1

        # if song has no playrecord
        # then ignore
        if (len(song.playrecord) == 0):
            setattr(song, calclevel_diff, 0)

        # smaller score is better
        # random walk for 5 times (for level)
        cur_lv = getattr(song, calclevel_diff)
        cur_weight = getattr(song, calcweight_diff)
        if (cur_lv>20):
            cur_lv = 20
            cur_weight = 10
        elif (cur_lv<0):    # too small value
            cur_lv = 0
            cur_weight = 10
        if (cur_weight > 20):
            cur_weight = 20
        elif (cur_weight < 1):
            cur_weight = 1
        lvls = [cur_lv,]
        scores = [getScore(song, lvls[0], cur_weight),]
        for t in range(iterate_time):
            new_level = cur_lv + random.uniform(_range[0], _range[1])
            lvls.append(new_level)
            scores.append(getScore(song, new_level, cur_weight))
        setattr(song, calclevel_diff, lvls[scores.index(min(scores))])

        # random walk for 5 times (for weight)
        cur_lv = getattr(song, calclevel_diff)
        lvls = [cur_weight,]
        scores = [getScore(song, cur_lv, lvls[0]),]
        for t in range(iterate_time):
            new_weight = cur_weight + random.uniform(_range[0], _range[1])*0.1*cur_weight
            lvls.append(new_weight)
            scores.append(getScore(song, cur_lv, new_weight))
        setattr(song, calcweight_diff, lvls[scores.index(min(scores))])

        error_sum += min(scores)
    return error_sum

def calculate_player(player, _range=(-0.5, 0.5), iterate_time=20):
    def getScore(player, level, type):
        cul = 0
        for precord in player.playrecord:
            if (precord.song.songtype[:2] != type): # check song type
                continue
            if (precord.playclear == 0):    # ignore noclear
                continue

            # get current clear state
            for diff in ["easy", "hd", "exh"]:
                calclevel = getattr(precord.song, 'calclevel_'+diff)
                if (calclevel < 2 or calclevel > 18):   # too low level or too high level is wrong calculated: ignore
                    continue
                v = clearScore(precord.playclear, diff)         # real value (model: expected)
                cul += (v - model_user(5, calclevel, level))**2 # weight is 5, maybe
        return cul

    # random walk for 10 times
    if (player.splevel < 0):
        player.splevel = 0
    lvls = [player.splevel,]
    scores = [getScore(player, lvls[0], "SP"),]
    for t in range(iterate_time):
        new_level = player.splevel + random.uniform(_range[0], _range[1])
        lvls.append(new_level)
        scores.append(getScore(player, new_level, "SP"))
    player.splevel = lvls[scores.index(min(scores))]

    # random walk for 10 times
    if (player.dplevel < 0):
        player.dplevel = 0
    lvls = [player.dplevel,]
    scores = [getScore(player, lvls[0], "DP"),]
    for t in range(iterate_time):
        new_level = player.dplevel + random.uniform(_range[0], _range[1])
        lvls.append(new_level)
        scores.append(getScore(player, new_level, "DP"))
    player.dplevel = lvls[scores.index(min(scores))]
    return min(scores)

# you need to commit manually
def calculate_player_by_name(iidxmeid, _range=(-0.5, 0.5), iterate_time=15):
    player = db.Player.query.filter_by(iidxmeid=iidxmeid).one()
    # in case of this player hadn't played any(or big difference), initalize it
    log.Print('initalize player level ...')
    calculate_player(player, (0, 20), 50)
    log.Print('detailing player level ...')
    calculate_player(player, (6, 6), 20)
    err = calculate_player(player, _range, iterate_time)
    return err

def iterate_player(_range=(-0.5, 0.5), iterate_time=5):
    i = 0
    players = db_session.query(db.Player).all()
    error_sum = 0
    for player in players:
        if (i%10==0):
            log.Print("%d/%d" % (i, len(players)))
        i+=1

        error_sum += calculate_player(player, _range, iterate_time)
    return error_sum

######################################
# initalize DB with zero value
def initDB_Zero():
    log.Print('initalizing to Zero ...')
    for song in db_session.query(db.Song).all():
        for d in diffs:
            setattr(song, "calclevel_"+d, 0)
            setattr(song, "calcweight_"+d, 0)

######################################
# initalize DB 
def initDB():
    # set inital values for calculation (song)
    log.Print('initalize ...')
    for song in db_session.query(db.Song).all():
        pclear = []
        for precord in song.playrecord:
            pclear.append(precord.playclear)
        # if no score data, then songlevel is 0 (unknown)
        if (len(pclear) == 0):
            for diff in diffs:
                setattr(song, 'calclevel_'+diff, 0)
                setattr(song, 'calcweight_'+diff, 10)
            continue

        # 1. check average clear score
        # high average, low difficulty
        pclear_score_avg = sum([clearScore(_c) for _c in pclear]) / float(len(pclear))

        # 2. check ratio of hard clear
        # high ratio of easy clear, high difficulty
        pclear.sort()
        i = 0
        for _c in pclear:
            if _c >= 5: # greedy method to check diff (hard difficulty)
                break
            i += 1
        # gather all the information
        for diff in diffs:
            setattr(song, 'calclevel_'+diff, song.songlevel + float(i)/len(pclear) + 1-pclear_score_avg)
            setattr(song, 'calcweight_'+diff, 10)   # default is 10

    # set inital values for calculation (player)
    # do MCMC like method to estimate player (wide range)
    for player in db_session.query(db.Player).all():
        player.splevel = 0  # init
        player.dplevel = 0  # init
    iterate_player((0, 13), 100)

    # show us a little graph
    #showSongStat()
    #showPlayerStat()

###########################################
#
# main func
#
###########################################

def calc_player_rough():
    log.Print("playerlevel_stabilizing_rough")
    for i in range(1):
        log.Print("iteration %d" % i)
        iterate_player((-14, 14), 20)

def calc_song_rough(d=None):
    log.Print("songlevel_stabilizing_rough")
    for i in range(1):
        log.Print("iteration %d" % i)
        if (d == None):
            d = diffs
        for diff in d:
            print diff
            iterate_song((-4, 4), 10, diff)

def calc_player_stable():
    log.Print("playerlevel_stabilizing")
    for i in range(30):
        log.Print("iteration %d" % i)
        iterate_player((-0.5, 0.5), 2)

def calc_song_stable(d=None):
    log.Print("songlevel_stabilizing")
    for i in range(30):
        log.Print("iteration %d" % i)
        if (d == None):
            d = diffs
        for diff in d:
            print diff
            iterate_song((-0.5, 0.5), 2, diff)

def calc_MCMC():
    for i in range(20):
        log.Print("iteration %d" % i)
        for diff in diffs:
            iterate_song((-0.5, 0.5), 3, diff)
        iterate_player((-0.5, 0.5), 3)
        if (True):
            log.Print('song')
            #showSongStat("SP", True, "songstatSP%d.png"%i)
            #showSongStat("DP", True, "songstatDP%d.png"%i)
            log.Print('player')
            showPlayerStat(True, "playerstat%d.png"%i)
        if ((i+1)%10 == 0):
            db_session.commit()

def main():
    # you may comment this initing process if it's bad
    #initDB()

    # make player stable
    calc_player_rough()
    calc_player_stable()
    db.commit()

    # make song stable
    calc_song_rough()
    calc_song_stable()
    db.commit()

    # full iteration
    calc_MCMC()

    log.Print('finished. closing DB ...')
    db.commit()
    db.remove()


if __name__=="__main__":
    main()
"""
