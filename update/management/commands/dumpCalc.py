from django.core.management import BaseCommand
import iidxrank.models as models
import json

def dump_json():
    lst_users = []
    lst_songs = []
    j = {'users':lst_users, 'songs':lst_songs}

    # parse users
    print 'user parsing ...'
    ignore_user_cnt = 0
    valid_user_cnt = 0
    for p in models.Player.objects.all():
        # ignore if pr_cnt is less than 20
        valid = 1
        if (p.playrecord_set.count() < 20):
            ignore_user_cnt += 1
            valid = 0
        valid_user_cnt += 1
        prs = []
        user = {
            'id': p.id,
            'iidxid': p.iidxid,
            'splevel': p.splevel,
            'dplevel': p.dplevel,
            'spclass': p.spclass,
            'dpclass': p.dpclass,
            'valid': valid,
            'prs': prs,
            }
        for pr in p.playrecord_set.all():
            prs.append( (pr.song.id, pr.playclear) )
        lst_users.append(user)
    print 'ignored users: %d, valid: %d' % (ignore_user_cnt, valid_user_cnt)
    

    # parse songs/prs
    print 'song parsing ...'
    ignore_song_cnt = 0
    valid_song_cnt = 0
    for s in models.Song.objects.all():
        valid = 1
        if (s.playrecord_set.count() < 10):
            ignore_song_cnt += 1
            valid = 0
        valid_song_cnt += 1
        ps = []
        song = {
            'id': s.id,
            'leasy': s.calclevel_easy,
            'weasy': s.calcweight_easy,
            'lhd': s.calclevel_hd,
            'whd': s.calcweight_hd,
            'lexh': s.calclevel_exh,
            'wexh': s.calcweight_exh,
            'valid': valid,
            'ps': ps
        }
        for pr in s.playrecord_set.all():
            ps.append( (pr.player.id, pr.playclear) )
    print 'ignored songs: %d, valid: %d' % (ignore_song_cnt, valid_song_cnt)
    return j

def load_json(j):
    lst_users = j['users']
    lst_songs = j['songs']

    # load users
    print 'user loading ...'
    for user in lst_users:
        obj = models.Player.filter(id=user['id']).first()
        if (obj == None):
            print 'id %d(%s) invalid data' % (user['id'], user['iidxid'])
            continue
        obj.splevel = user['splevel']
        obj.dplevel = user['dplevel']
        obj.save()
    print len(lst_users)

    # load songs
    print 'song loading ...'
    for song in lst_songs:
        obj = models.Song.filter(id=song['id']).first()
        if (obj == None):
            print 'song %d invalid data' % song['id']
            continue
        obj.save()
    print len(lst_songs)


class Command(BaseCommand):
    help = """dump song/user level/clear info into json file for calculation"""

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)
        parser.add_argument('--action', default='dump', help='dump / load')

    def handle(self, *args, **options):
        if (options['action'] == 'dump'):
            self.dump(options['path'])
        elif (options['action'] == 'load'):
            self.load(options['path'])
        else:
            raise Exception('invalid action')

    def dump(self, path):
        j = dump_json()
        with open(path, 'w') as f:
            print 'output file: ', options['path']
            json.dump(j, f)

    def load(self, path):
        with open(path, 'r') as f:
            j = json.load(f)
        load_json(j)
        print 'loading done.'
