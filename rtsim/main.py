# -*- encoding: utf-8 -*-
import sys
import gpxpy
from dateutil import tz
from time import mktime, sleep


def submit(p):
    print 'submit',
    print p.latitude, p.longitude, p.speed, p.time.isoformat()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'usage: %s gpx_file.gpx [time divider]' % sys.argv[0]
        sys.exit(1)

    speedup = 1
    if len(sys.argv) > 2:
        speedup = int(sys.argv[2])

    f = open(sys.argv[1], 'r')
    gpx = gpxpy.parse(f)
    f.close()

    last = None
    for track in gpx.tracks:
        for segment in track.segments:
            for p in segment.points:
                p.time = p.time.replace(tzinfo=tz.tzlocal())
                cur_timestamp = mktime(p.time.timetuple())
                if not last:
                    submit(p)
                else:
                    print 'sleeping %i seconds' % ((cur_timestamp - last) / speedup)
                    sleep((cur_timestamp - last) / speedup)
                    submit(p)
                last = cur_timestamp
