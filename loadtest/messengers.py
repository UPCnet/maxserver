import requests
import json
import re
from datetime import datetime

from gevent.monkey import patch_all
from socketIO_client import SocketIO
import gevent

patch_all()


class SocketIOMessenger(object):
    def __init__(self, url, port, maxurl, maxport, username, conversation, namespace='/max'):
        self.url = url
        self.port = port
        self.schema = 'https' if self.port == 443 else 'http'
        self.maxurl = maxurl
        self.maxport = maxport
        self.maxschema = 'https' if self.maxport == 443 else 'http'
        self.username = username
        self.conversation = conversation
        self.ns = namespace
        self.join()

        self.listen_event('listening')
        self.listen_event('people')
        self.listen_event('joined')
        self.listen_event('update')

        self.emit('join', {'username': self.username, 'timestamp': self.timestamp()})

        self.setHeaders()

        self.total_received = 0
        self.total_elapsed = 0
        self.joined = 0

    def timestamp(self):
        ts = int(float(datetime.now().strftime('%s.%f')) * 1000)
        return ts

    def setHeaders(self):
        self.headers = {
            'X-Oauth-Token': '54601948560149560',
            'X-Oauth-Username': self.username,
            'X-Oauth-Scope': 'widgetcli',
        }

    def notify(self, stime, r, **kwargs):
        #print '%s sent' % self.username
        self.emit('message', {'conversation': self.conversation, 'timestamp': stime})

    def sendMessage(self, message):
        payload = {
            "object": {
            "objectType": "note",
            "content": message
            }
        }
        from functools import partial
        req_start = datetime.now().isoformat()
        callback = partial(self.notify, req_start)
        self.notify(req_start, None)

        requests.post(
            '{}://{}:{}/conversations/{}/messages'.format(self.maxschema, self.maxurl, self.maxport, self.conversation),
            data=json.dumps(payload),
            headers=self.headers,
            hooks=dict(response=callback)
        )

    def on_people(self, *args):
        #print '%d in room' % args[0]['inroom']
        self.joined = args[0]['inroom']

    def on_joined(self, *args):
        #print '%s joined %s in conversation %s' % (args[0]['username'], self.username, args[0]['conversation'])
        pass

    def on_listening(self, *args):
        #print '%s is listening on conversations %s' % (self.username, args[0]['conversations'])
        pass

    def on_update(self, *args):
        #print 'New message on conversation from %s, %s refreshes' % (args[0]['username'], self.username)
        now = datetime.now()
        emited = datetime.strptime(args[0]['timestamp'], "%Y-%m-%dT%H:%M:%S.%f")
        elapsed = now - emited

        self.total_elapsed += elapsed.total_seconds()
        self.total_received += 1


class WebsocketMessenger(SocketIOMessenger):

    def listen_event(self, event):
        event_listener = getattr(self, 'on_%s' % event)
        self.namespace.on(event, event_listener)

    def emit(self, event, payload):
        self.namespace.emit(event, payload)

    def join(self):
        self.socket = SocketIO(self.url, self.port)
        self.namespace = self.socket.connect(self.ns)


class PollingMessenger(SocketIOMessenger):

    def listen_event(self, event):
        pass

    def emit(self, event, payload):
        resp = requests.post(self.getURL(), data='5::%s:{"name":"%s","args":[%s]}' % (self.ns, event, json.dumps(payload, sort_keys=True).replace(' ', '')))

    def join(self):
        self.sessionid = None
        resp = requests.get(self.getURL())
        self.sessionid, heartbeat, timeout, transports = resp.text.split(':')
        self.heartbeat_timeout = int(heartbeat)
        self.timeout = int(timeout)
        self.transports = transports.split(',')

        # Fix transport
        resp = requests.get(self.getURL())

        #Connect to namespace
        resp = requests.post(self.getURL(), data='1::%s:' % self.ns)
        if resp.status_code != 200:
            print 'connect', resp.status_code
        gevent.spawn(self.eventListener)
        gevent.spawn(self.heartbeat)

    def getURL(self):
        params = {
            'timestamp': self.timestamp(),
            'part': '' if self.sessionid is None else 'xhr-polling/{}'.format(self.sessionid),
            'schema': self.schema,
            'url': self.url,
            'port': self.port,

        }
        return '{schema}://{url}:{port}/socket.io/1/{part}?t={timestamp}'.format(**params)

    def heartbeat(self):
        requests.post(self.getURL(), data='2::')
        gevent.sleep(40)

    def eventListener(self):
        while True:
            gevent.sleep(0.5)
            resp = requests.get(
                self.getURL(),
            )
            if resp.text.startswith(u'\ufffd'):
                events = [json.loads(event) for messageid, endpoint, event in re.findall(u'\ufffd\d+\ufffd5:(.*?):(.*?):([^\ufffd]*)', resp.text)]
            else:
                events = [json.loads(event) for messageid, endpoint, event in re.findall(u'5:(.*?):(.*?):(.*?)\s*$', resp.text)]
            for event in events:
                event_listener = getattr(self, 'on_%s' % event['name'], None)
                if event_listener is not None:
                    event_listener(event['args'][0])
