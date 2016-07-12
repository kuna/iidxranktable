#-*- coding: utf-8 -*-
# site: clddal.kr
# DEPRECIATED ONE

from bs4 import BeautifulSoup
import urllib

def parse():
	# common
	data = urllib.urlopen("http://clddal.kr/list/kuna/12")
	soup = BeautifulSoup(data)

	res = []	# [(group, [song name, ..]), ..]
	table = soup.find('table', id='music_list')
	trs = table.find_all('tr')
	current_group = None
	group_title = ''
	for tr in trs:
		if (tr['class'][0] == u'row_header'):
			continue
		if (tr['class'][0] == u'row_empty'):
			continue
		if (tr['class'][0] == u'row_group_title'):
			group_title = tr.get_text()
			current_group = (group_title, [])
			res.append( current_group )
			continue

		tds = tr.find_all('td')
		title = tds[1].find_all('span')[0].get_text()
		diff = tds[1].find_all('span')[0]['class'][0]
		if (diff == "df0"):
			diff = "SPN"
		elif (diff == "df1"):
			diff = "SPH"
		elif (diff == "df2"):
			diff = "SPA"
		current_group[1].append( (title, diff) )

	return res

#print parse()