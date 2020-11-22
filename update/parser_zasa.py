#-*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib
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

def parse6():
	return parse("6")

def parse7():
	return parse("7")

def parse8():
	return parse("8")

def parse9():
	return parse("9")

def parse10():
	return parse("10")

def parse11():
	return parse("11")

def parse12():
	return parse("12")

def parse(diff):
	# common
	# http://stackoverflow.com/questions/17509607/submitting-to-a-web-form-using-python
	formdata = {
		'env': 'a230',
		'submit': '%E8%A1%A8%E7%A4%BA',#u'表示',
		'cat': 0,
		'mode': 'p1',
		'offi': diff,
		}
	formdata_raw = urllib.urlencode(formdata)
	req = urllib.Request("http://zasa.sakura.ne.jp/dp/rank.php", formdata_raw)
	data = urllib.request.urlopen(req).read()
	soup = BeautifulSoup(data, "lxml")	# depress warning - parser 'lxml'

	res = []	# [(group, [song name, ..]), ..]
	table = soup.find('table', class_="rank_p1")
	trs = table.find_all('tr')
	group_title = ''
	for tr in trs[1:-1]:
		# first col: diff group
		group_title = tr.find_all('td')[0].get_text()

		spns = tr.find_all('span')
		for sp in spns:
			sp_text = sp.get_text()
			title = sp_text[:-4]
			diff = "DP" + sp['class'][0].upper()
			if (diff == "DPL"):
				diff = "DPA"
				title += " (L)"
			group = getGroup(res, group_title)
			group[1].append( (title, diff) )

	return res


