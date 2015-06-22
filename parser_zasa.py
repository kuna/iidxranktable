#-*- coding: utf-8 -*-
# site: http://clickagain.sakura.ne.jp/cgi-bin/sort11/data.cgi?level10=1&mix=1

from bs4 import BeautifulSoup
import urllib, urllib2
import re

def getGroup(arr, g):
	for ele in arr:
		if (ele[0] == g):
			return ele
	# if not, add group
	new_group = (g, [])
	arr.append( new_group )
	return new_group

#
# ==================================================================
#

def parse10():
	return parse("10", "10")

def parse11():
	return parse("11", "11")

def parse12():
	return parse("12", "12")

def parse(dif1, dif2):
	# common
	# http://stackoverflow.com/questions/17509607/submitting-to-a-web-form-using-python
	formdata = {'reg': 'a220',
		'cat[]': '[13, 5, 79]',
		#'submit': u'表示',
		'dif1': dif1,
		'dif2': dif2,
		'votelink': '1',
		'rank1': '1',
		'rank2': '13',
		'mode': 'p4',
		'ver1': '010',
		'ver2': '220',
		'rowWidth': '0'
		}
	formdata_raw = urllib.urlencode(formdata)
	req = urllib2.Request("http://zasa.sakura.ne.jp/2dxdp/rank_view.php", formdata_raw)
	data = urllib2.urlopen(req).read()
	soup = BeautifulSoup(data)

	res = []	# [(group, [song name, ..]), ..]
	table = soup.find('table').find_all('table')[1]
	trs = table.find_all('tr')
	group_title = ''
	idx = 0
	for tr in trs:
		idx += 1
		# ignore first row (thead)
		if (idx <= 1):
			continue

		# first col: diff group
		group_title = tr.find_all('td')[0].get_text()

		spns = tr.find_all('span', class_='POINT')
		for sp in spns:
			sp_text = sp.find('span').get_text()
			title = sp_text[:-4]
			diff = "DP" + sp.find('span')['class'][0]
			group = getGroup(res, group_title)
			group[1].append( (title, diff) )

	return res

