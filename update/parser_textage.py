#-*- coding: utf-8 -*-
import io, json
import jsondata
import urllib
import re
import codecs
from bs4 import BeautifulSoup

USE_CACHE = True

#
# only textage returns html string
# (dont use this version, as javascript file is not handled properly)
#
def crawl_(version):
    url = 'http://textage.cc/score/';
    html = ''
    if (version >= 0):
        versionstr = '0'
        if (version >= 10):
            versionstr = 'A'
            version -= 10
        versionstr = chr(ord(versionstr) + version)
        url = 'http://textage.cc/score/?v%s11B00' % versionstr
    try:
        data = urllib.urlopen(url)
        html = data.read()
        data.close()
    except Exception as e:
        print e
    return html

def crawl(version):
    urls = ['http://textage.cc/score/actbl.js',
            'http://textage.cc/score/titletbl.js']
    jsontxt = ''

    if (USE_CACHE):
        #
        # as site's textage format is so bad ...
        # we manually made file instead of parsing.
        # to update, type to browser console:
        #
        # s = JSON.stringify({"actbl":actbl, "titletbl":titletbl})
        # copy(s)
        #
        # and upload it to server.
        #
        with codecs.open('textage.json', 'rb', encoding='utf-8') as f:
            jsontxt = f.read()
    else:
        # -- make javascript into json --
        for url in urls:
            data = urllib.urlopen(url)
            js = data.read()
            for line in js.split('\n'):
                t = line
                if (t[:2] == '//'): # remove comment
                    continue
                if (len(t) == 0):
                    continue
                if (t[:4] == 'A=10'): # tricky case ignore ...
                    continue
                # assign op. to colon (tricky)
                p = t.find('=')
                if (p >= 0 and p < 20):
                    t = t[:p] + ':' + t[p+1:]
                # make attribute name properly
                if (t[0] == '\''):
                    p = t.find('\'', 1)
                    t = '\"' + t[1:p] + '\"' + t[p+2:]
                elif (t[0] != '\"'):
                    p = t.find(':')
                    t = '\"' + t[:p] + '\"' + t[p:]
                # semicolon to comma
                p = t.find(';')
                if (p >= 0):
                    jsontxt += t[:p] + ',\n'
                else:
                    jsontxt += t + '\n'
        jsontxt = '{\n' + jsontxt + '\n}'
        # XXX: may need to comment out?
        with open('textage.json', 'w') as f:
            f.write(jsontxt)

    return jsontxt

#
# parse textage site and get musicdata
#
def parse(version):
    jsontxt = crawl(version)
    d = json.loads(jsontxt)
    musicdata = []
    cleanr = re.compile('<.*?>')
    try:
        actbl = d['actbl']          # is_old,?,?,?,?,SPN,?,SPH,?,SPA,?,DPL,?,?,?,DPN,?,DPH,?,DPA,?,DPL,?
        titletbl = d['titletbl']    # series, id, is_comment, genre, artist, title
        for songid,meta in titletbl.items():
            if (songid not in actbl):
                continue
            if (meta[0] != version): # is version match?
                continue
            linfo = actbl[songid]
            if (linfo[0] == 2): # is old?
                continue
            levels = (linfo[5], linfo[7], linfo[9], linfo[11], linfo[15], linfo[17], linfo[19], linfo[21])
            title_str = re.sub(cleanr, '', meta[5]).encode('utf-8')
            playtypes = ('SPN', 'SPH', 'SPA', 'SPL', 'DPN', 'DPH', 'DPA', 'DPL')
            d  = {}
            obj_id = 100000 + meta[1] # TODO: compatible with iidx.me later ..?
            d['title'] = title_str
            d['level'] = 0
            d['diff'] = ''
            d['version'] = version
            for lvl,playtype in zip(levels, playtypes):
                # XXX: we ignore level below 10 on purpose to reduce DB weight
                # XXX: must ignore level 0 - it means not-existing-chart
                if (lvl < 10):
                    continue
                obj = d.copy()
                #obj['data'] = dd
                obj['level'] = lvl
                obj['clear'] = 0
                obj['score'] = 0
                obj['notes'] = 0
                obj['miss'] = 0
                obj['id'] = obj_id
                obj['diff'] = playtype
                # if playtype is SPL / DPL, then add leggendary mark
                if (playtype == 'SPL' or playtype == 'DPL'):
                    obj['title'] = title_str + '†'
                musicdata.append(obj)
    except Exception as e:
        print e
    return musicdata
