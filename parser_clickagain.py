#-*- coding: utf-8 -*-
# site: http://clickagain.sakura.ne.jp/cgi-bin/sort11/data.cgi?level10=1&mix=1

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

def processTitle(input):
	# clickagain's title is so chaos...
	# we need to change it
	# remove braket and trim
	# CF: timepiece phase (CN ver) ... -> SOLVED
	return re.sub(r"\(\(.*?\)\)", '', input.replace(u"（", '((').replace(u"）", '))')).strip()

#
# ==================================================================
#

def parse10():
	return parse("10AC", "http://clickagain.sakura.ne.jp/cgi-bin/sort11/data.cgi?level10=1&mix=1")

def parse11():
	return parse("11AC", "http://clickagain.sakura.ne.jp/cgi-bin/sort11/data.cgi?level11=1&mix=1")

def parse12():
	return parse("12AC", "http://clickagain.sakura.ne.jp/cgi-bin/sort11/data.cgi?level12=1&mix=1")

def parse12_7():
	# common
	data = urllib.urlopen("http://clickagain.sakura.ne.jp/cgi-bin/sort11/data.cgi?level12=1")
	soup = BeautifulSoup(data)

	res = []	# [(group, [song name, ..]), ..]
	table = soup.find_all('table')[5]
	trs = table.find_all('tr')
	group_name = 1
	group_idx = 1
	idx = 0
	for tr in trs:
		idx += 1
		if (idx <= 4):
			continue

		# 0:ver, 1:title, 5:normal, 6:hard, 7:op1P, 8:op2P, 9:desc
		tds = tr.find_all('td')
		if (len(tds) < 9):
			# group
			# if group idx = 8 (that means 8기) then must exit
			if (group_idx >= 8):
				break
			group_name = str(group_idx) + u'기'
			group_idx += 1
			continue
		title = processTitle(tds[1].get_text())
		diff = tds[1]['style']
		if (diff.find("red") >= 0):
			diff = "SPA"
		elif (diff.find("orange") >= 0):
			diff = "SPH"
		elif (diff.find("#0066FF") >= 0):
			diff = "SPN"
		else:
			diff = "SPA"
		group = getGroup(res, group_name)
		group[1].append( (title, diff) )

	return res

def parse(tableID, uri):
	# common
	data = urllib.urlopen(uri)
	soup = BeautifulSoup(data)

	res = []	# [(group, [song name, ..]), ..]
	table = soup.find('table', id=tableID)
	trs = table.find_all('tr')
	for tr in trs:
		if (('class' in tr) and tr['class'][0] == u'top'):
			continue

		# 0:ver, 1:title, 5:normal, 6:hard, 7:op1P, 8:op2P, 9:desc
		tds = tr.find_all('td')
		if (len(tds) < 9):
			break
		title = processTitle(tds[1].get_text())
		if (title == "title"):
			continue
		diff = tds[1]['style']
		if (diff.find("red") >= 0):
			diff = "SPA"
		elif (diff.find("orange") >= 0):
			diff = "SPH"
		elif (diff.find("#0066FF") >= 0):
			diff = "SPN"
		else:
			diff = "SPA"
		lv = tds[6].get_text()
		group = getGroup(res, lv)
		group[1].append( (title, diff) )

	return res

#print parse12_7()