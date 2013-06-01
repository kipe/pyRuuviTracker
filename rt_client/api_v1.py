import hashlib
import hmac
import requests
import json
from datetime import datetime


class RT_Client:
    ''' Client for RuuviTracker API v1 '''
    API_VERSION = 1
    USER_AGENT = 'RuuviTracker Python Client API v1/0.1'

    def __init__(
            self,
            tracker_code,
            shared_secret,
            url,
            session_code=None,
            debug=False):
        ''' Initialize RuuviTracker Client '''
        self.tracker_code = tracker_code
        self.shared_secret = shared_secret
        self.url = url
        self.session_code = session_code
        self.debug = debug

    def __macInput(self, data):
        ''' Generate input for HMac calculation '''
        m = ''
        for key in sorted(data.iterkeys()):
            value = data[key]
            m += key
            m += ':'
            m += str(value)
            m += '|'
        if self.debug:
            print 'macInput:',
            print m
        return m

    def __makeQuery(self, data):
        ''' Make query to RuuviTracker server '''
        headers = {
            'User-Agent': self.USER_AGENT,
            'Content-type': 'application/json'
        }
        if self.debug:
            print 'Sending data:',
            print data
        r = requests.post(self.url, headers=headers, data=json.dumps(data))
        if self.debug:
            print 'Server response:',
            print r.status_code, r.text
        return r.status_code

    def _computeHMac(self, data):
        ''' Calculate HMac for message '''
        digest = hmac.new(self.shared_secret, digestmod=hashlib.sha1)
        digest.update(self.__macInput(data))
        return digest.hexdigest()

    def _createMessage(self, data):
        ''' Create message to send to server '''
        data['version'] = self.API_VERSION
        data['tracker_code'] = self.tracker_code
        data['mac'] = self._computeHMac(data)
        return data

    def sendMessage(self, data):
        ''' Sends message to server. Argument "data" must be an instance of RT_Data '''
        if not isinstance(data, RT_Data):
            if self.debug:
                print 'Incompatible datatype, use RT_Data'
            return

        data = self._createMessage(data.buildData())
        return self.__makeQuery(data)


class RT_Data:
    ''' Data instance for RuuviTracker '''
    def __init__(
            self, latitude=None, longitude=None, time=None,
            accuracy=None, vertical_accuracy=None, heading=None,
            satellite_count=None, battery=None, speed=None,
            altitude=None, temperature=None, annotation=None):
        self.latitude = latitude
        self.longitude = longitude
        self.time = time
        self.accuracy = accuracy
        self.vertical_accuracy = vertical_accuracy
        self.heading = heading
        self.satellite_count = satellite_count
        self.battery = battery
        self.speed = speed
        self.altitude = altitude
        self.temperature = temperature
        self.annotation = annotation
        self.extra = dict()

    def buildData(self):
        ''' Builds data-dictionary suitable for RuuviTracker server '''
        def removeNonASCII(s):
            return "".join(i for i in s if ord(i) < 128).replace(' ', '-')

        data = dict()
        # latitude can be a float (62.8723) or string (6284.21,N)
        if self.latitude:
            data['latitude'] = self.latitude
        # longitude can be a float (28.8723) or string (2884.21,N)
        if self.longitude:
            data['longitude'] = self.longitude
        if self.time:
            # if instance of datetime is passed, format it according to the spec
            if type(self.time) == datetime:
                data['time'] = self.time.strftime('%Y-%m-%dT%H:%M:%S.000%z')
            # else trust that the user has done the required measures to format it
            else:
                data['time'] = str(self.time)
        if self.accuracy:
            data['accuracy'] = float(self.latitude)
        if self.vertical_accuracy:
            data['vertical_accuracy'] = float(self.vertical_accuracy)
        if self.heading:
            data['heading'] = float(self.heading)
        if self.satellite_count:
            data['satellite_count'] = int(self.satellite_count)
        if self.battery:
            data['battery'] = float(self.battery)
        if self.speed:
            data['speed'] = float(self.speed)
        if self.altitude:
            data['altitude'] = float(self.altitude)
        if self.temperature:
            data['temperature'] = float(self.temperature)
        if self.annotation:
            data['annotation'] = str(self.annotation)
        if self.extra and type(self.extra) == dict:
            for k, v in self.extra.iteritems():
                k = removeNonASCII(k)
                if k.startswith('X-'):
                    data['%s' % k] = v
                else:
                    data['X-%s' % k] = v
        return data
