#-*- coding: utf-8 -*-
import io, json
import jsondata
import urllib
from bs4 import BeautifulSoup

#
# parse_users: return user lists
#
def parse_users():
    def parse_users_page(num, arr):
        def getUsers(soup, arr):
            names = soup.find_all(class_="djname")
            iidxids = soup.find_all(class_="iidxid")
            i = 0
            for (name, iidxid) in zip(names, iidxids):
                if (i>0):
                    iidxmeid = name.find('a')['href'].replace("/", "")
                    arr.append( (name.get_text(), iidxmeid, iidxid.get_text()) )
                i+= 1

        data = urllib.urlopen("http://iidx.me/!/userlist/?page=%d" % num)
        soup = BeautifulSoup(data.read())
        getUsers(soup, arr)

    def getPageCount():
        data = urllib.urlopen("http://iidx.me/!/userlist/")
        soup = BeautifulSoup(data.read())
        page = soup.find_all(class_="page")
        return int(page[len(page)-1].get_text())
    
    pcnt = getPageCount()
    r = []
    for i in range(1, pcnt+1):
        print 'parsing page %d ...' % i
        parse_users_page(i, r)
    return r

#
# parse_user: return user info (includes song)
# (djname, iidxid, ...)
#
def parse_user(username, mode, level):
    parsedata = jsondata.loadJSONurl("http://json.iidx.me/%s/%s/level/%d/" % (username, mode, level))

    return parsedata

#
# parse_user: return user info (only user info)
# (djname, iidxmeid, iidxid)
#
def parse_userinfo(username):
    parsedata = jsondata.loadJSONurl("http://json.iidx.me/%s/recent/" % username)
    if parsedata == None:
        return None
    else:
        return ( parsedata['userdata']['djname'], username, parsedata['userdata']['iidxid'] )

#
# parse_songs: return songs in level
# (title, level, notes, version, diff, id ...)
#
def parse_songs(level, mode):
    parsedata = jsondata.loadJSONurl("http://json.iidx.me/delmitz/%s/level/%d/" % (mode, level))

    # remove scores
    ret = []
    #del parsedata['userdata']
    #del parsedata['status']
    for music in parsedata['musicdata']:
        #del music['clear']
        #del music['score']
        #del music['miss']
        music['data']['diff'] = music['data']['diff'].upper()
        ret.append(music['data'])

    return ret





##
# (use ONLY when json isn't working)
#
def parse_iidxme_http(url):
    userdata = {}
    musicdata = []
    r = {'userdata': userdata, 'musicdata': musicdata}
    try:
        data = urllib.urlopen(url)
        soup = BeautifulSoup(data.read())
        # userdata part
        userobj = soup.find('div', attrs={'id': 'playernav_toggle'})
        userdata['djname'] = userobj.find('div', class_='djname').get_text().strip()
        userdata['iidxid'] = userobj.find('div', class_='iidxid').get_text().strip()
        userdata['spclass'] = userobj.find('div', class_='spclass').find('span')['class'][1][5:]
        userdata['dpclass'] = userobj.find('div', class_='dpclass').find('span')['class'][1][5:]
        contentobj = soup.find('div', attrs={'id': 'content'})
        modeobj = contentobj.find('p')
        mode = modeobj['class'][1]
        # musicdata part
        musicobj = contentobj.find('div', class_='musiclist')
        for tr in musicobj.findAll('div', class_='tr')[1:]:
            cells = tr.findAll('div', class_='td')
            obj = {}
            if (len(cells) == 0 or 'separator' in cells[0]['class'] or 'th' in cells[0]['class']):
                continue
            _, _, clr, diffchar = cells[0]['class']
            _, _, _, lvstr = cells[1]['class']
            obj['clear'] = int(clr.replace('clear', ''))
            obj['data'] = {}
            obj['data']['level'] = int(lvstr[2:])
            obj['data']['diff'] = mode + diffchar
            obj['data']['title'] = cells[2].get_text()
            obj['data']['version'] = 24     # IMPORTANT! this is hardcoded, so must use for recent.
            obj['data']['id'] = int( cells[2].find('a')['href'].split('/')[-1])
            try:
                obj['data']['notes'] = int(cells[3].get_text())
            except ValueError:
                obj['data']['notes'] = 0
            obj['rate'] = float(cells[7].find('span').get_text()[:-1])
            try:
                obj['miss'] = int(cells[8].get_text())
            except ValueError:
                obj['miss'] = 0
            musicdata.append(obj)
    except Exception as e:
        print e
    return r

def parse_user_http(username, mode, level):
    return parse_iidxme_http("http://iidx.me/%s/%s/level/%d/" % (username, mode, level))

def parse_userinfo_http(username):
    parsedata = parse_user_http(username, 'sp', 10)
    if parsedata == None:
        return None
    else:
        return ( parsedata['userdata']['djname'], username, parsedata['userdata']['iidxid'] )

def parse_songs_http():
    urls = [
        'http://iidx.me/delmitz/sp/ver/24/normal',
        'http://iidx.me/delmitz/sp/ver/24/hyper',
        'http://iidx.me/delmitz/sp/ver/24/another',
        'http://iidx.me/delmitz/dp/ver/24/normal',
        'http://iidx.me/delmitz/dp/ver/24/hyper',
        'http://iidx.me/delmitz/dp/ver/24/another',
#        'http://iidx.me/delmitz/sp/level/leggendaria',
#        'http://iidx.me/delmitz/dp/level/leggendaria',
        ]
    ret = []
    # remove scores
    for url in urls:
        parsedata = parse_iidxme_http(url)
        for music in parsedata['musicdata']:
            music['data']['diff'] = music['data']['diff'].upper()
            ret.append(music['data'])
    return ret
