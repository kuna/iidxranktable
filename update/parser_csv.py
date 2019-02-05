# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
import iidxrank.models as models
import iidxrank.rankpage as rankpage
import csv

def open(filepath, username, type_="SP", log=[]):
    # find user from db first
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return False
    # open CSV file
    with open(filepath, 'r') as f:
        tbl = csv.reader(f, delimiter=',')
        update(tbl, type_, user)
    return True

def update(tbl, type_, user, log=[]):
    def clrstr2clr(s):
        clrstrs = [
            "NO PLAY",
            "FAILED",
            "ASSIST CLEAR",
            "EASY CLEAR",
            "CLEAR",
            "HARD CLEAR",
            "EX HARD CLEAR",
            "FULLCOMBO CLEAR"
        ]
        # -- XXX: should throw SEVERE error here
        #         (but blocked now ...)
        if (s not in clrstrs):
            return 0
        return clrstrs.index(s)
    def gen_recs(l): # len 7
        diff = 0 if l[0]=="" else int(l[0])
        exscore = int(l[1])
        clear = clrstr2clr(l[5])
        return {'clear':clear, 'score':exscore, 'diff':diff}
    player = rankpage.get_player_from_user(user, True)
    rec_success = 0
    rec_tot = 0
    for row in list(tbl)[1:]:
        songname=row[1]
        recs=[ gen_recs(row[5:11]), gen_recs(row[12:18]), gen_recs(row[19:25]) ]
        dfs=["NORMAL", "HYPER", "ANOTHER"]
        for rec,df in zip(recs,dfs):
            rec_tot = rec_tot + 1
            try:
                # change type if necessary (leggendaria)
                type_cur = type_
                if (songname.endswith('†') or songname.endswith('†LEGGENDARIA')):
                    type_cur = type_+'L'
                else:
                    type_cur = type_+df[0]
                song = models.Song.objects.get(songtitle=songname, songtype=type_cur)
            except models.Song.DoesNotExist:
                sn = songname.decode('utf-8')
                log.append("Invalid song '%s' (%s)" % (sn, type_cur))
                continue
            if (not rankpage.update_record(song.id, player, rec)):
                sn = songname.decode('utf-8')
                log.append("Failed to update song '%s' (%s)" % (sn, df))
                continue
            rec_success = rec_success + 1
    log.append("Updated %d records out of %d." % (rec_success, rec_tot))
