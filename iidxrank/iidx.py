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

classes = (
    (1, u'-'),
    (2, u'七級'),
    (3, u'六級'),
    (4, u'五級'),
    (5, u'四級'),
    (6, u'三級'),
    (7, u'二級'),
    (8, u'一級'),
    (9, u'初段'),
    (10, u'二段'),
    (11, u'三段'),
    (12, u'四段'),
    (13, u'五段'),
    (14, u'六段'),
    (15, u'七段'),
    (16, u'八段'),
    (17, u'九段'),
    (18, u'十段'),
    (19, u"中伝"),
    (20, u"皆伝"),
    )

def getdanstring(dan):
    for cls in classes:
        if (cls[0] == dan):
            return cls[1]
    return None

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
