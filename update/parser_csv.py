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
    tbllst = list(tbl)
    dfs=["NORMAL", "HYPER", "ANOTHER", "LEGGENDARIA"]
    dfs_col_no = {}
    for df in dfs:
        dfs_col_no[df] = []
        col_no = 0
        for col in tbllst[0]:
            if (col.startswith(df)):
                dfs_col_no[df].append(col_no)
            col_no += 1
        if (len(dfs_col_no[df]) != 7):
            log.append("Difficulty %s column count is not 7 (will be ignored)." % df)
    for row in tbllst[1:]:
        songname=row[1]
        recs = []
        for df in dfs:
            dfs_col = []
            for i in dfs_col_no[df]:
                dfs_col.append(row[i])
            if (len(dfs_col) == 7):
                recs.append( gen_recs(dfs_col) )
            else:
                recs.append( {'clear': 0, 'score': 0, 'diff': 0} )
        for rec,df in zip(recs,dfs):
            if (rec['diff'] == 0):
                continue    # level-zero is invalid song, ignore silently.
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
