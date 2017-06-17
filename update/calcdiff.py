import tensorflow as tf
import json

_DEBUG_MSG = False

# @description
# sess: tf sess
# data: (array of [songlvl, clear]) : MUST sort with songlvl! (ascending)
# cnt: iterate count (exact of sigmoid result)
#
# @return (esti_lv, esti_beta, error)
def learn_userlvl(sess, data, cnt, use_top_cnt=10):
  # similar with songlvl learning
  # but we check user's approx level with top10 songs average clear score
  clr_level = []
  for d in reversed(data):
    if (d[1] > 0):
      clr_level.append(d[0])
      if (len(clr_level) >= use_top_cnt):
        break
  clr_level_avg = sum(clr_level) / len(clr_level)
  if (_DEBUG_MSG):
    print 'EXPECTED LVL:', clr_level_avg
    if (len(clr_level) < use_top_cnt):
      print '[WARNING] clr level data feature is too small'
  return learn_songlvl(sess, clr_level_avg, data, cnt, 1)

# @description
# sess: tf sess
# songlvl: current songlvl (desired value, integer)
# data: (array of [songlvl, clear])
# cnt: iterate count (exact of sigmoid result)
#
# @return (esti_lv, esti_beta, error)
def learn_songlvl(sess, songlvl, data, cnt, reverse=-1):
  arr_lv_data = []
  arr_clr_data = []
  for d in data:
    arr_lv_data.append(d[0])
    arr_clr_data.append(d[1])
  lv_dim = len(arr_lv_data)
  LV_DATA = tf.placeholder(tf.float32, lv_dim)  # LV of users
  CLR_DATA = tf.placeholder(tf.float32, lv_dim) # CLEAR stat(0,1) of users
  LV = tf.placeholder(tf.float32, 1)            # LV of song (static)
  X = tf.Variable(tf.zeros([1]))                # LV of song (to learn)
  Y = tf.Variable(tf.ones([1]))                 # variety of song (to learn)
  # W_SIG: calculate sigmoid errors by users
  LV_DELTA = X-LV_DATA
  V_SIG = tf.sigmoid(LV_DELTA*Y*reverse)                    # sigmoid values
  D_SIG = tf.square(tf.subtract(V_SIG, CLR_DATA))   # sq(sigmoid - CLEAR stat) = error
  W_SIG = tf.reduce_sum(D_SIG)                      # reduce error to 1x1 = weight
  # W_LVL: to prevent begin outfit from current level
  W_LVL = tf.square(X-LV)*0.05
  # TOTAL WEIGHT & learn
  W = tf.add(W_SIG, W_LVL)
  #W = W_SIG
  #opti = tf.train.AdagradOptimizer(100)
  opti = tf.train.GradientDescentOptimizer(1)
  train = opti.minimize(W)
  feed_dict={
    LV_DATA: arr_lv_data,
    CLR_DATA: arr_clr_data,
    LV: [songlvl],
    }
  sess.run(tf.global_variables_initializer())
  sess.run(X.assign([songlvl]))   # initializer for fast-score estimate
  sess.run(Y.assign([3]))           # initializer for fast-score estimate
  for i in range(cnt):
    sess.run(train, feed_dict=feed_dict)
  if (_DEBUG_MSG):
    print 'LV_DELTA',(sess.run(LV_DELTA,feed_dict=feed_dict))
    print 'WANT RESULT',(sess.run(CLR_DATA,feed_dict=feed_dict))
    print 'SIG RESULT',(sess.run(V_SIG,feed_dict=feed_dict))
  r = (sess.run(X,feed_dict=feed_dict), 
      sess.run(Y,feed_dict=feed_dict), 
      sess.run(W,feed_dict=feed_dict))
  return r



# utils for digesting raw json fi
def digest_jsondata(j, initslevel=False):
  lst_users = j['users']
  lst_songs = j['songs']
  d_users = {}
  for u in lst_users:
    d_users[u['id']] = u
  d_songs = {}
  for s in lst_songs:
    d_songs[s['id']] = s
    if (initslevel):
      s.calclevel_easy = s.level
      s.calclevel_hd = s.level+0.2
      s.calclevel_exh = s.level+0.4
      s.calcweight_easy = 3
      s.calcweight_hd = 3
      s.calcweight_exh = 3
  r = {'users':d_users, 'songs':d_songs}
  return r



# clear: 3 easy 5 hd 6 exh
def get_user_data(user, d_songs, stype='sp', onlyvalid=True):
  data = []
  for sid,clear in user['prs']:  # song id, clear
    s = d_songs[sid]
    if (onlyvalid and not s['valid']):
      pass
    if (s['type'] != stype):
      continue
    if (c >= 6):
      data.append( (s.calclevel_exh,1) )
    elif (c >= 5):
      data.append( (s.calclevel_hd,1) )
    elif (c >= 3):
      data.append( (s.calclevel_easy,1) )
    else:
      data.append( (s.calclevel_easy,0) )
  # sort data (ascending)
  return sorted(data, key=itemgetter(0))


def get_song_data(song, d_users, clear, onlyvalid=True):
  data = []
  for uid,uclear in song['ps']:
    stype = song['type']  # is song SP or DP?
    if (onlyvalid and not d_users[uid]['valid'+stype]):
      continue
    c = 1
    if (uclear < clear):
      c = 0
    data.append( (d_users[uid][stype+'level'], c) )
  return data


def calc_user_data(sess, user, d_songs):
  itercnt = 10
  data = get_user_data(user, d_songs, 'sp')
  user['spclass'] = learn_userlvl(sess, data, itercnt)
  data = get_user_data(user, d_songs, 'dp')
  user['dpclass'] = learn_userlvl(sess, data, itercnt)

def calc_song_data(sess, song, d_users):
  itercnt = 10
  songlvl = song['level']
  data = get_song_data(song, d_users, 3)
  song['calclevel_easy'], song['calcweight_easy'], _ = learn_songlvl(sess, songlvl, data, itercnt)
  data = get_song_data(song, d_users, 5)
  song['calclevel_hd'], song['calcweight_hd'], _ = learn_songlvl(sess, songlvl, data, itercnt)
  data = get_song_data(song, d_users, 6)
  song['calclevel_exh'], song['calcweight_exh'], _ = learn_songlvl(sess, songlvl, data, itercnt)

def calc_users(sess, d_users, d_songs):
  for uid,user in d_users.items():
    calc_user_data(sess, user, d_songs)
def calc_songs(sess, d_users, d_songs):
  for sid,song in d_users.items():
    calc_song_data(sess, song, d_users)


# calc modify original data so be careful
def calc(j, itercnt=100, initslevel=False):
  # digest for calculation
  dj = digest_jsondata(j)
  d_users = dj['users']
  d_songs = dj['songs']
  print d_songs.keys()

  sess = tf.Session()
  for i in range(itercnt):
    calc_users(sess, d_users, d_songs)  # should calculate user first with song data
    calc_songs(sess, d_users, d_songs)
    print 'iter %d' % i

def calcdumpfile(fpath):
  print 'loading ...'
  with open(fpath) as f:
    j = json.load(f)
  print 'calculating ...'
  calc(j)
  print 'writing ...'
  with open(fpath, 'w') as f:
    json.dump(j,f)

# -----

# @description test for tensorflow module
def test_songlvl():
  sess = tf.Session()

  # song lvl : 11
  songlvl = 11
  itercnt = 10
  # general song diff test
  data=[
      [10,0],
      [10,0],
      [10,0],
      [11,1],
      [11,1],
      [11,0],
      [12,1],
      [12,1],
      ]
  print learn_songlvl(sess, songlvl, data, itercnt)

  # no failure test 
  data=[
      [10,1],
      [10,1],
      [10,1],
      [11,1],
      [11,1],
      [11,1],
      [12,1],
      [12,1],
      ]
  print learn_songlvl(sess, songlvl, data, itercnt)

  # no clear test 
  data=[
      [10,0],
      [10,0],
      [10,0],
      [11,0],
      [11,0],
      [11,0],
      [12,0],
      [12,0],
      ]
  print learn_songlvl(sess, songlvl, data, itercnt)

  # large-variance test (TODO)
  data=[
      [10,0],
      [10,0],
      [10,0],
      [11,0],
      [11,1],
      [11,0],
      [12,0],
      [12,0],
      [12,1],
      [12,1],
      ]
  print learn_songlvl(sess, songlvl, data, itercnt)

  # too little data test (TODO)


# @description test for tensorflow module
def test_userlvl():
  sess = tf.Session()

  # song lvl : 11
  songlvl = 11
  itercnt = 10
  # general song diff test
  print 'general test - 1 unclear song'
  data=[
      [10,1],
      [10,1],
      [10,0],
      [11,1],
      [11,1],
      [11,1],
      [12.2,1],
      [12.3,0],
      [12.4,0],
      ]
  print learn_userlvl(sess, data, itercnt, 2)

  # general song diff test 2
  print 'general test - all cleared before 11'
  data=[
      [10,1],
      [10,1],
      [10,1],
      [11,1],
      [11,1],
      [11,1],
      [12.2,1],
      [12.3,0],
      [12.4,0],
      ]
  print learn_userlvl(sess, data, itercnt, 2)

  # all clear test
  print 'all cleared user'
  data=[
      [10,1],
      [10,1],
      [10,1],
      [11,1],
      [11,1],
      [11,1],
      [12.2,1],
      [12.3,1],
      [12.4,1],
      ]
  print learn_userlvl(sess, data, itercnt, 2)


import sys
if (__name__ == "__main__"):
  if (len(sys.argv) == 1):
    print "run algorithm validation test"
    test_songlvl()
    #test_userlvl()
  else:
    fn = sys.argv[1]
    print 'fn: %s' % fn
    calcdumpfile(fn)
