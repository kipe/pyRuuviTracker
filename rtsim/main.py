# -*- encoding: utf-8 -*-
import sys
import gpxpy
from dateutil import tz
from time import mktime, sleep
from random import randint
from rt_client import RT_Client, RT_Data


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print 'usage: %s tracker_code shared_secret gpx_file.gpx [time divider]' % sys.argv[0]
        sys.exit(1)

    # initialize variables from command line
    tracker_code = sys.argv[1]
    shared_secret = sys.argv[2]
    gpx_file = sys.argv[3]

    # set speedup
    speedup = 1
    if len(sys.argv) > 4:
        speedup = int(sys.argv[4])

    # parse GPX file
    f = open(gpx_file, 'r')
    gpx = gpxpy.parse(f)
    f.close()

    # initialize RuuviTracker Client
    rt = RT_Client(
        tracker_code,
        shared_secret,
        'http://dev-server.ruuvitracker.fi/api/v1-dev/events',
        debug=True)
    # set session name
    rt.session_code = 'TestSession_%i' % randint(1, 30000)

    # initialize last points timestamp as None
    last = None
    # loop through tracks in the GPX-file
    for track in gpx.tracks:
        # loop through segments in the track
        for segment in track.segments:
            # loop through points in segment
            for p in segment.points:
                # gpxpy doesn't parse tzinfo correctly, so replace it with local
                p.time = p.time.replace(tzinfo=tz.tzlocal())
                # get the current unix-timestamp
                cur_timestamp = mktime(p.time.timetuple())
                # if last timestamp isn't None
                if last is not None:
                    # sleep for the correct time (simulate real time divided by speedup)
                    print 'sleeping %i seconds' % ((cur_timestamp - last) / speedup)
                    sleep((cur_timestamp - last) / speedup)
                # create RT_Data object from the GPX point
                #   data available in 'test.gpx' is lat, lon, time, speed and elevation
                d = RT_Data(
                    p.latitude, p.longitude, p.time,
                    speed=p.speed, altitude=p.elevation)
                # send the RT_Data -object to server
                rt.sendMessage(d)
                # set last point timestamp to current
                last = cur_timestamp
