import requests
import json
from datetime import datetime

from gevent.monkey import patch_all
from socketIO_client import SocketIO

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
        self.join(namespace)

        self.listen_event('listening')
        self.listen_event('people')
        self.listen_event('joined')
        self.listen_event('update')

        self.emit('join', {'username': self.username, 'timestamp': self.timestamp()})

        self.setHeaders()

        self.total_received = 0
        self.total_elapsed = 0
        self.joined = 1

    def timestamp(self):
        return int(float(datetime.now().strftime('%s.%f')) * 1000)

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


class WebsocketMessenger(SocketIOMessenger):

    def listen_event(self, event):
        event_listener = getattr(self, 'on_%s' % event)
        self.namespace.on('joined', event_listener)

    def emit(self, event, payload):
        self.namespace.emit(event, payload)

    def join(self, namespace):
        self.socket = SocketIO(self.url, self.port)
        self.namespace = self.socket.connect(namespace)

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
