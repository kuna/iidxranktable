#-*- coding: utf-8 -*-
import io, json
import urllib
from bs4 import BeautifulSoup
from update import jsondata

VERSION=25

#
# parse_users: return user lists
#
def parse_users(page_limit=999):
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
        soup = BeautifulSoup(data.read(), "lxml")
        getUsers(soup, arr)

    def getPageCount():
        data = urllib.urlopen("http://iidx.me/!/userlist/")
        soup = BeautifulSoup(data.read(), "lxml")
        page = soup.find_all(class_="page")
        return int(page[len(page)-1].get_text())
    
    pcnt = getPageCount()
    r = []
    for i in range(1, pcnt+1):
        if (i > page_limit):
            break
        print('parsing page %d ...' % i)
        parse_users_page(i, r)
    return r

#
# parse_user: return user info (includes song)
# (djname, iidxid, ...)
#
"""
def parse_user(username, mode, level):
    parsedata = jsondata.loadJSONurl("http://json.iidx.me/%s/%s/level/%d/" % (username, mode, level))
    return parsedata
"""

def parse_user_recent(username):
    data = []
    return data

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
def parse_iidxme_http_musicdata(html):
    musicdata = []
    try:
        soup = BeautifulSoup(html, "lxml")
        contentobj = soup.find('div', attrs={'id': 'content'})
        modeobj = contentobj.find('p')
        mode = modeobj['class'][1]
        musicobj = contentobj.find('div', class_='table')   # musiclist
        for tr in musicobj.findAll('div', class_='tr')[1:]:
            cells = tr.findAll('div', class_='td')
            obj = {}
            if (len(cells) == 0 or 'separator' in cells[0]['class'] or 'th' in cells[0]['class']):
                continue
            _, _, clr, _ = cells[0]['class']
            _, _, diffchar, lvstr = cells[1]['class']
            obj['clear'] = int(clr.replace('clear', ''))
            obj['score'] = 0    # TODO- it's quite hard...
            obj['data'] = {}
            obj['data']['level'] = int(lvstr[2:])
            obj['data']['diff'] = (mode + diffchar).upper()
            obj['data']['title'] = cells[2].get_text()
            obj['data']['id'] = int( cells[2].find('a')['href'].split('/')[-1])
            obj['data']['version'] = 0    # TODO- maybe impossible to get exact one?
            title_aobj = cells[2].find('a')
            title_cls = title_aobj.get('class')
            if (title_cls and title_cls[0] == 'newmusic'):
                obj['data']['version'] = VERSION
            try:
                obj['data']['notes'] = int(cells[3].get_text())
            except ValueError:
                obj['data']['notes'] = 0
            if ('noscore' in cells[6]['class']):
                obj['score'] = 0
            else:
                obj['score'] = int(cells[6].find('span',class_='scorenum').get_text())
            obj['rate'] = float(cells[7].find('span').get_text()[:-1])
            try:
                obj['miss'] = int(cells[8].get_text())
            except ValueError:
                obj['miss'] = 0
            musicdata.append(obj)
    except Exception as e:
        print(e)
    return musicdata

def parse_iidxme_songdata(url):
    data = urllib.urlopen(url)
    html = data.read()
    data.close()
    musicdata = []

    soup = BeautifulSoup(html, "lxml")
    contentobj = soup.find('div', attrs={'id': 'content'})
    _genre = contentobj.find('p', class_='genre').get_text()
    _title = contentobj.find('p', class_='title').get_text()
    _artist = contentobj.find('p', class_='artist').get_text()
    _id = int( url.split('/')[-1])
    _types = ["SP", "DP"]
    _typeidx = 0
    for table in contentobj.findAll('div', class_='table musicdata'):
        mode = _types[_typeidx]
        _typeidx += 1
        for tr in table.findAll('div', class_='tr')[1:-2]:
            cells = tr.findAll('div', class_='td')
            if (len(cells) == 0
                    or 'separator' in cells[0]['class']
                    or 'detail' in cells[0]['class']
                    or 'th' in cells[0]['class']):
                continue
            # if result cell, not song cell? --> go to next cell
            if (len(cells[0]['class']) <= 3):
                continue
            obj = {}
            _, _, clr, _ = cells[0]['class']
            _, _, diffchar, lvstr = cells[1]['class']
            obj['clear'] = int(clr.replace('clear', ''))
            obj['score'] = 0    # TODO- it's quite hard...
            obj['data'] = {}
            obj['data']['level'] = int(lvstr[2:])
            obj['data']['diff'] = (mode + diffchar).upper()
            obj['data']['title'] = _title
            obj['data']['id'] = _id
            obj['data']['version'] = VERSION
            try:
                obj['data']['notes'] = int(cells[2].get_text())
            except ValueError:
                obj['data']['notes'] = 0
            if ('noscore' in cells[6]['class']):
                obj['score'] = 0
            else:
                obj['score'] = int(cells[6].find('span',class_='scorenum').get_text())
            obj['rate'] = float(cells[7].find('span').get_text()[:-1])
            try:
                obj['miss'] = int(cells[8].get_text())
            except ValueError:
                obj['miss'] = 0
            musicdata.append(obj)
            
    return musicdata

def parse_iidxme_http(url):
    userdata = {}
    musicdata = []
    r = {'userdata': userdata, 'musicdata': musicdata, 'status': 'success'}
    try:
        data = urllib.urlopen(url)
        html = data.read()
        data.close()
        soup = BeautifulSoup(html, "lxml")
        # userdata part
        userobj = soup.find('div', attrs={'id': 'playernav_toggle'})
        userdata['iidxmeid'] = url.replace('http://','').replace('https://','').split('/')[1]
        userdata['djname'] = userobj.find('div', class_='djname').get_text().strip()
        userdata['iidxid'] = userobj.find('div', class_='iidxid').get_text().strip()
        userdata['spclass'] = int(userobj.find('div', class_='spclass').find('span')['class'][1][5:])
        userdata['dpclass'] = int(userobj.find('div', class_='dpclass').find('span')['class'][1][5:])
        # musicdata part
        # if multipage, then parse them all
        contentobj = soup.find('div', attrs={'id': 'content'})
        pagerobj = contentobj.find('div', class_='pager')
        if (pagerobj):
            pagesobj = pagerobj.findAll('a')
        else:
            pagesobj = []
        musicdata += parse_iidxme_http_musicdata(html)
        for aobj in pagesobj:
            try:
                url = aobj['href']
                if (url[0] == '/'):
                    url = 'http://iidx.me' + url
                data_page = urllib.urlopen(url)
                musicdata += parse_iidxme_http_musicdata(data_page.read())
            except Exception as e:
                print(e)
    except Exception as e:
        # maybe temporaral server connection error, or invalid user
        print(e)
        r = {'status': 'failed'}
    return r

def parse_user_http(username, mode, level):
    return parse_iidxme_http("http://iidx.me/%s/%s/level/%d/" % (username, mode, level))

def parse_userinfo_http(username):
    parsedata = parse_user_http(username, 'sp', 10)
    if parsedata == None:
        return None
    else:
        return ( parsedata['userdata']['djname'], username, parsedata['userdata']['iidxid'] )

def parse_songs_http(username='delmitz', ver=25):
    urls = [
        'http://iidx.me/%s/sp/ver/%d/normal' % (username,ver),
        'http://iidx.me/%s/sp/ver/%d/hyper' % (username,ver),
        'http://iidx.me/%s/sp/ver/%d/another' % (username,ver),
        'http://iidx.me/%s/dp/ver/%d/normal' % (username,ver),
        'http://iidx.me/%s/dp/ver/%d/hyper' % (username,ver),
        'http://iidx.me/%s/dp/ver/%d/another' % (username,ver),
        'http://iidx.me/%s/sp/level/leggendaria' % (username),
        'http://iidx.me/%s/dp/level/leggendaria' % (username),
        ]
    ret = []
    # remove scores
    for url in urls:
        parsedata = parse_iidxme_http(url)
        if ('musicdata' not in parsedata):
            raise Exception('Failed to retrieve data from iidx.me');
        for music in parsedata['musicdata']:
            music['data']['diff'] = music['data']['diff'].upper()
            ret.append(music['data'])
    return ret

def parse_qpro(username):
    url = "http://iidx.me/%s" % username
    try:
        data = urllib.urlopen(url)
        html = data.read()
        data.close()
        soup = BeautifulSoup(html, "lxml")
        return "http://iidx.me" + soup.find('div', class_='qpro').find('img')['src']
    except Exception as e:
        print(e)
        return None
