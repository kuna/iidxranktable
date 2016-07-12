#-*- coding: utf-8 -*-

import parser_clickagain, parser_zasa, parser_iidxme, parser_custom
import textdistance
import datetime
from django.db import transaction
import log
import iidxrank.models as models

def update_iidxme():
    def update(data):
        added_data = 0
        for song in data:
# if not exists, then add
# if exists, then check level and title, then update.
            obj_song = models.Song.objects.filter(songid=song['id'], songtype=song['diff']).first()
            if obj_song == None:
                if (song['notes'] == None):
                    song['notes'] = 0

                obj_song = models.Song.objects.create(songtitle=song['title'], 
                    songtype=song['diff'],
                    songid=song['id'],
                    songlevel=song['level'],
                    songnotes=song['notes'],
                    version=song['version'],
                    calclevel_easy=0,
                    calcweight_easy=0,
                    calclevel_normal=0,
                    calcweight_normal=0,
                    calclevel_hd=0,
                    calcweight_hd=0,
                    calclevel_exh=0,
                    calcweight_exh=0)
                added_data = added_data+1
            else:
                if (obj_song.songlevel != song['level'] or
                        obj_song.version != song['version'] or
                        obj_song.songtitle != song['title']):
                    log.Print("song %s updated" % song['title'])
                    obj_song.songlevel = song['level']
                    obj_song.version = song['version']
                    obj_song.songtitle = song['title']
                    obj_song.save()
        log.Print("added %d datas" % added_data)

    for lvl in range(6, 13):
        log.Print('parsing iidxme sp (%d)' % lvl)
        data = parser_iidxme.parse_songs(lvl, "sp")
        update(data)

    for lvl in range(6, 13):
        log.Print('parsing iidxme dp (%d)' % lvl)
        data = parser_iidxme.parse_songs(lvl, "dp")
        update(data)

# update or create rank table
# (depreciated)
def updateDB(data, tablename, tabletitle, level):
    added_data = 0

    # get table first
    table = models.RankTable.query.filter_by(tablename=tablename)
    if (not table.count()):
        table = models.RankTable(tablename=tablename,
            tabletitle=tabletitle,
            level=level)
        db_session.add(table)
    else:
        table = table.one()
        # update table info
        table.tabletitle = tabletitle
        table.level = level
        table.time = datetime.datetime.now()

    # process rankitems/rankcategories
    for group in data:
        # before adding items, get category first
        category = models.RankCategory.query.filter_by(ranktable_id=table.id, categoryname=group[0])
        if (not category.count()):
            category = models.RankCategory(ranktable_id=table.id, categoryname=group[0])
            # append category to group
            table.category.append(category)
            db_session.add(category)
        else:
            category = category.one()

        # make rank item
        # if already exists then update category only
        for item in group[1]:
            try:
                song_tag = item[0] + "," + item[1]
                rankitem = db_session.query(models.RankItem).filter_by(rankcategory=category, info=song_tag)
                if not rankitem.count():
                    ###########################################
                    # search song automatically from DB
                    song = models.Song.query.filter_by(songtitle=item[0], songtype=item[1], songlevel=level)
                    if (not song.count()):
                        song = smart_suggestion(item[0], item[1], level)    # name, diff, level
                        if (song == None):
                            continue    # ignore
                    else:
                        song = song.one()
                    # check once more, if same song is already exists in ranktable
                    # if it does, then cancel add new one
                    rankitem_query = db_session.query(models.RankItem)\
                        .join(models.RankItem.rankcategory)\
                        .filter(models.RankCategory.ranktable==table, models.RankItem.song==song)
                    if (rankitem_query.count()):
                        log.Print('same song already exists in rank table!')
                        log.Print('just modifying tag/category...')
                        rankitem = rankitem_query.one()
                        rankitem.info = song_tag
                        rankitem.rankcategory_id = category.id
                        continue
                    #############################################

                    rankitem = models.RankItem(info=song_tag, rankcategory_id=category.id, song_id=song.id)
                    # append item to category
                    category.rankitem.append(rankitem)
                    db_session.add(rankitem)
                    added_data = added_data+1
                else:
                    rankitem = rankitem.one()
                    rankitem.rankcategory_id = category.id
            except Exception as e:
                print 'error occured: %s' % e, item

    log.Print("added %d datas" % added_data)

#
# (depreciated)
# don't used site
#
def update_SP():
    log.Print('parsing 2ch')
    updateDB(parser_custom.parse12(), "SP12_2ch", 
        u"Beatmania IIDX SP lv.12 Hard Guage Rank", 12)
    log.Print('parsing clickagain')
    updateDB(parser_clickagain.parse12_7(), "SP12_7", 
        u"Beatmania IIDX SP lv.12 7記 Hard Guage Rank", 12)
    updateDB(parser_clickagain.parse12(), "SP12", 
        u"Beatmania IIDX SP lv.12 Hard Guage Rank", 12)
    updateDB(parser_clickagain.parse11(), "SP11", 
        u"Beatmania IIDX SP lv.11 Hard Guage Rank", 11)
    updateDB(parser_clickagain.parse10(), "SP10", 
        u"Beatmania IIDX SP lv.10 Hard Guage Rank", 10)
    updateDB(parser_clickagain.parse9(), "SP9", 
        u"Beatmania IIDX SP lv.9 Hard Guage Rank", 9)
    updateDB(parser_clickagain.parse8(), "SP8", 
        u"Beatmania IIDX SP lv.8 Hard Guage Rank", 8)
    # groove
    updateDB(parser_clickagain.parse12N(), "SP12N", 
        u"Beatmania IIDX SP lv.12 Normal Guage Rank", 12)
    updateDB(parser_clickagain.parse11N(), "SP11N", 
        u"Beatmania IIDX SP lv.11 Normal Guage Rank", 11)
    updateDB(parser_clickagain.parse10N(), "SP10N", 
        u"Beatmania IIDX SP lv.10 Normal Guage Rank", 10)
    updateDB(parser_clickagain.parse9N(), "SP9N", 
        u"Beatmania IIDX SP lv.9 Normal Guage Rank", 9)
    updateDB(parser_clickagain.parse8N(), "SP8N", 
        u"Beatmania IIDX SP lv.8 Normal Guage Rank", 8)

def update_DP():
    log.Print('parsing zasa')
    updateDB(parser_zasa.parse12(), "DP12", 
        u"Beatmania IIDX DP lv.12 Rank", 12)
    updateDB(parser_zasa.parse11(), "DP11", 
        u"Beatmania IIDX DP lv.11 Rank", 11) 
    updateDB(parser_zasa.parse10(), "DP10", 
        u"Beatmania IIDX DP lv.10 Rank", 10) 
    updateDB(parser_zasa.parse9(), "DP9", 
        u"Beatmania IIDX DP lv.9 Rank", 9) 
    updateDB(parser_zasa.parse8(), "DP8", 
        u"Beatmania IIDX DP lv.8 Rank", 8) 
#   updateDB(parser_zasa.parse7(), "DP7", 
#       u"Beatmania IIDX DP lv.7 Rank", 7) 
#   updateDB(parser_zasa.parse6(), "DP6", 
#       u"Beatmania IIDX DP lv.6 Rank", 6)

#
# suggest similar song object from name/diff
#
def smart_suggestion(name, diff, level):
    import sys
    # first get all song data
    songs = models.Song.query.filter_by(songtype=diff)\
        .filter(models.Song.songlevel == level)

    # make new array for suggestion
    title_arr = []
    for item in songs:
        title_arr.append(item.songtitle)

    # and call 'textdistance'
    suggestions = textdistance.getNearTextDistance(title_arr, name)[:5]

    # remake song array
    #sug_songs = []
    #for sug_title in suggestions:
    #   sug_songs.append()

    while (1):
        log.Print("cannot find <%s / %s>" % (name.encode('utf-8'), diff))
        log.Print("but some suggestion was found")
        idx = 1
        log.Print("0. (deleted)")
        for sug_title in suggestions:
            log.Print("%d. %s (%s)" % (idx, sug_title[0].encode('utf-8'), diff))
            idx += 1
        log.Print("enter the song you want or enter song code you want in negative")
        log.Print("(ex: -23456)")
        code = 0
        try:
            code = int(raw_input("> "))
        except ValueError:
            log.Print("enter correct value")
            continue

        if (code == 0):
            return None
        elif (code > 0):
            if (code > len(suggestions)):
                log.Print('out of suggestions')
                continue
            return models.Song.query.filter_by(songtype=diff, songtitle=suggestions[code-1][0]).one()
        elif (code < 0):
            # search song which that code exists
            songs = models.Song.query.filter_by(songtype=diff, songid=-code)
            # if not then loop again
            if not songs.count():
                log.Print('no song of such code exists')
                continue
            else:
                song = songs.one()
                log.Print('you selected song [%s]. if okay then [y]' % song.songtitle.encode('utf-8'))
                okay = raw_input("> ")
                if (okay == "y"):
                    return song
                else:
                    log.Print('canceled.')
                    continue

#
# make relation with song
# depreciated
# don't use
#
def update_relation():
    log.Print('making relation with song table ...')
    # scan rankitem one by one
    updated_cnt = 0
    for item in models.RankItem.query.all():
        if (item.song_id == None):
            # if song_id not set, scan it
            log.Print('current: %s' % item.songtitle)
            songs = models.Song.objects.filter(songtitle=item.songtitle, songtype=item.songtype)
            if songs.count() <= 0:
                # do smart suggestion
                song = smart_suggestion(item.songtitle, item.songtype, item.category.ranktable.level)
                if song == None:
                    continue
                item.song_id = song.id
                song.save()
            else:
                song = songs.first()
                #song.rankitem.append(item)
                item.song_id = song.id
        updated_cnt += 1

    log.Print("%d items updated." % updated_cnt)

"""
def main():
    #
    # you should execute it through IDLE because of unicode
    # (if you're windows)
    #

    update_iidxme()

    update_DP()

    log.Print('finished. closing DB ...')
    db.commit()
    db.remove()

if __name__ == '__main__':
    main()
"""
