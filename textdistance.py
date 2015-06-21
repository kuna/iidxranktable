#-*- coding: utf-8 -*-
#
# textdistance.py
# used Levenshtein distance
#

# getTextDistance(a, b)
# => get text distance from each other
# used to recognize new song's id (matching song name)
#
from operator import itemgetter

def getTextDistance(a_, b_):
	# before start, modify text in proper mode (same uppercase etc..)
	# TODO add replace?
	a = a_.upper()
	b = b_.upper()

	# remove redundant space and etc...
	a = a.replace(' ', '')
	b = b.replace(' ', '')

	# cutting string to short one makes good result in most case.
	str_len = len(a)
	if (len(b) < str_len):
		str_len = len(b)
	a = a[:str_len]
	b = b[:str_len]

	# (a, b) sized int array
	arr = [[0 for x in range(len(b)+1)] for x in range(len(a)+1)]

	# init int
	for i in range(len(a)):
		arr[i+1][0] = i+1
	for j in range(len(b)):
		arr[0][j+1] = j+1

	# calculate
	for j in range(1, len(b)+1):
		for i in range(1, len(a)+1):
			if a[i-1] == b[j-1]:
				arr[i][j] = arr[i-1][j-1]
			else:
				arr[i][j] = min(arr[i-1][j]+1, arr[i][j-1]+1, arr[i-1][j-1]+1)

	# longer sequence seems more reliable
	return float(arr[len(a)][len(b)]) / str_len

#
# getNearTextDistance
# sort by nearest text
#
def getNearTextDistance(arr, target):
	# make new array
	r_arr = []
	for t in arr:
		r_arr.append( (t, getTextDistance(t, target)) )

	return sorted(r_arr, key=itemgetter(1), reverse=False)

# you can try these codes -
#print getTextDistance("abcd", "bcd")
#print getTextDistance("abcd", "wer")
#print getNearTextDistance(["stoic （ストイコ）", "Spica （スピカ）"], "Spica")