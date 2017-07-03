# dper related code
import models

def copy_as_dbr(song_pk):
    # attempt to get object
    try:
        song_obj = models.Song.objects.get(id=song_pk)
    except Exception as e:
        return (False, 'invalid song id')
    # check is already DBR
    if (song_obj.songtype[:3].upper() == 'DBR'):
        return (False, 'song is already DBR')
    # check is songtype DP
    if (song_obj.songtype[:2].upper() != 'SP'):
        return (False, 'only SP songtype can be used as DBR.')
    # add new object
    lvl = song_obj.songlevel
    chartdiff = song_obj.songtype[-1].upper()
    models.Song.objects.create(
        songid = song_obj.songid,
        songtitle = '%s (%d%s)' % (song_obj.songtitle, lvl, chartdiff),
        songtype = 'DBR%s' % chartdiff,
        songlevel = 0,
        songnotes = song_obj.songnotes*2,
        version = song_obj.version,
        original = song_obj,
        tag = song_obj.songtitle)
    return (True, 'done.')
