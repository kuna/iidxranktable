#-*- coding: utf-8 -*-

def getclearstring(clear):
	if (clear == 0):
		return u'NO_PLAY'
	elif (clear == 1):
		return u'FAILED'
	elif (clear == 2):
		return u'ASSIST_CLEAR'
	elif (clear == 3):
		return u'EASY_CLEAR'
	elif (clear == 4):
		return u'CLEAR'
	elif (clear == 5):
		return u'HARD_CLEAR'
	elif (clear == 6):
		return u'EX-HARD_CLEAR'
	elif (clear == 7):
		return u'FULL_COMBO'
	return None

def getclearstring_simple(clear):
	if (clear == 0):
		return u'NOPLAY'
	elif (clear == 1):
		return u'FAILED'
	elif (clear == 2):
		return u'ASSIST'
	elif (clear == 3):
		return u'EASY'
	elif (clear == 4):
		return u'GROOVE'
	elif (clear == 5):
		return u'HC'
	elif (clear == 6):
		return u'EXH'
	elif (clear == 7):
		return u'FC'
	return None


def getdanstring(dan):
	if (dan == 1):
		return u"-"
	elif (dan == 2):
		return u"七級"
	elif (dan == 3):
		return u"六級"
	elif (dan == 4):
		return u"五級"
	elif (dan == 5):
		return u"四級"
	elif (dan == 6):
		return u"三級"
	elif (dan == 7):
		return u"二級"
	elif (dan == 8):
		return u"一級"
	elif (dan == 9):
		return u"初段"
	elif (dan == 10):
		return u"二段"
	elif (dan == 11):
		return u"三段"
	elif (dan == 12):
		return u"四段"
	elif (dan == 13):
		return u"五段"
	elif (dan == 14):
		return u"六段"
	elif (dan == 15):
		return u"七段"
	elif (dan == 16):
		return u"八段"
	elif (dan == 17):
		return u"九段"
	elif (dan == 18):
		return u"十段"
	elif (dan == 19):
		return u"中伝"
	elif (dan == 20):
		return u"皆伝"

def getrank(rate):
	if (rate >= 8.0/9*100):
		return u"AAA"
	elif (rate >= 7.0/9*100):
		return u"AA"
	elif (rate >= 6.0/9*100):
		return u"A"
	elif (rate >= 5.0/9*100):
		return u"B"
	elif (rate >= 4.0/9*100):
		return u"C"
	elif (rate >= 3.0/9*100):
		return u"D"
	elif (rate >= 2.0/9*100):
		return u"E"
	else:
		return u"F"

def diff_linear_conv(d):
	pass
