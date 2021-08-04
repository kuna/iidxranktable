#-*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib
import wikitextparser as wtp

def urlopen_read(url):
    html = ''
    try:
        data = urllib.request.urlopen(url)
        html = data.read()
        data.close()
    except Exception as e:
        print(e)
    return html

def trim_remywiki_text(text):
    r = []
    for line in text.split('\n'):
        if (line.startswith("{{IIDX Song|") or line.startswith("{{IIDX NC Song|")):
            r.append(line)
    return '\n'.join(r)

def fetch_remywiki_source(url):
    soup = BeautifulSoup(urlopen_read(url))
    tarea = soup.find("textarea").text
    # kind of trick: parse lines start with "{{IIDX Song|" or "{{IIDX NC Song|"
    wp = wtp.parse(trim_remywiki_text(tarea))
    return wp.templates

def try_int(s):
    try:
        s = s.replace("\'\'\'", "")
        if (s.startswith("LS=") or s.startswith("LD=")):
            s = s[3:]
        return int(s)
    except:
        return 0

def get_songs_from_remywiki_source(templates):
    title_list = []
    for t in templates:
        if (t.parent() != None):
            continue    # parse only topmost nodes
        if (t.name == 'IIDX Song'):
            genre = wtp.parse(t.arguments[0].value).plain_text()
            title = wtp.parse(t.arguments[1].value.split('<br>')[0]).plain_text()
            artist = wtp.parse(t.arguments[2].value).plain_text()
            # 3: bpm
            # 4: beginner
            diff_spn = try_int(t.arguments[5].value)
            diff_sph = try_int(t.arguments[6].value)
            diff_spa = try_int(t.arguments[7].value)
            diff_spl = try_int(t.arguments[8].value)
            diff_dpn = try_int(t.arguments[9].value)
            diff_dph = try_int(t.arguments[10].value)
            diff_dpa = try_int(t.arguments[11].value)
            diff_dpl = try_int(t.arguments[12].value)
        elif (t.name == 'IIDX NC Song'):
            if (len(t.arguments) < 10):
                continue
            genre = ''
            title = wtp.parse(t.arguments[0].value).plain_text()
            artist = ''
            diff_spn = try_int(t.arguments[3].value)
            diff_sph = try_int(t.arguments[4].value)
            diff_spa = try_int(t.arguments[5].value)
            diff_spl = try_int(t.arguments[6].value)
            diff_dpn = try_int(t.arguments[7].value)
            diff_dph = try_int(t.arguments[8].value)
            diff_dpa = try_int(t.arguments[9].value)
            diff_dpl = try_int(t.arguments[10].value)
        else:
            print('Warn: Unknown type \"%s\", ignored' % t.name)
            continue
        if (diff_spn == 0 and diff_sph == 0 and diff_spa == 0 and diff_spl == 0):
            # don't add to list if all charts are empty
            print('Warn: All difficulty infomation is empty \"%s\", ignored' % title)
            continue
        if (title in title_list):
            # don't add to list in case of duplicated song
            print('Warn: Duplicated song \"%s\", ignored.' % title)
            continue
        title_list.append(title)
        yield {
            'name': t.name,
            'title': title,
            'artist': artist,
            'genre': genre,
            'sp': (diff_spn, diff_sph, diff_spa, diff_spl),
            'dp': (diff_dpn, diff_dph, diff_dpa, diff_dpl)
            }

#
# parse remywiki and get musicdata
#
def parse(version):
    version_title_preset = [
        '',     # 0
        '',
        '',
        '',
        '',
        '',     # 5
        '',
        '',
        '',
        '',
        '',     # 10
        '',
        '',
        '',
        '',
        '',     # 15
        '',
        '',
        '',
        '',
        '',     # 20
        '',
        '',
        '',
        '',
        '',     # 25
        'Rootage',
        'HEROIC_VERSE',
        'BISTROVER',
        '',
        '',
    ]
    version_title = version_title_preset[version]
    if (version_title == ''):
        raise Exception('Version(%d) information of remiwiki is empty!' % version)
    url = 'https://remywiki.com/index.php?title=AC_%s&action=edit' % version_title
    songs = get_songs_from_remywiki_source(fetch_remywiki_source(url))
    playtypes = ('SPN', 'SPH', 'SPA', 'SPL', 'DPN', 'DPH', 'DPA', 'DPL')
    musicdata = []
    idx = 0
    for song in songs:
        d = {}
        obj_id = 100000 + idx # TODO: compatible with iidx.me later ..?
        d['title'] = song['title']
        d['level'] = 0
        d['diff'] = ''
        d['version'] = version
        levels = song['sp'] + song['dp']
        for lvl,playtype in zip(levels, playtypes):
            # XXX: we ignore level below 10 on purpose to reduce DB weight
            # XXX: must ignore level 0 - it means not-existing-chart
            if (lvl < 10):
                continue
            obj = d.copy()
            obj['level'] = lvl
            obj['clear'] = 0
            obj['score'] = 0
            obj['notes'] = 0
            obj['miss'] = 0
            obj['id'] = obj_id
            obj['diff'] = playtype
            # if playtype is SPL / DPL, then add leggendary mark
            if (playtype == 'SPL' or playtype == 'DPL'):
                obj['title'] = song['title'] + '†'
            musicdata.append(obj)
        idx += 1
    return musicdata
