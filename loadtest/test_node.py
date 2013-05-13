import sys
import requests
import json
from datetime import datetime

import gevent
from gevent.event import Event
from gevent.monkey import patch_all
from socketIO_client import SocketIO
import signal
import time
import json
import re
from messengers import WebsocketMessenger
patch_all()


class LongpollingMessenger(object):

    def timestamp(self):
        return int(float(datetime.now().strftime('%s.%f')) * 1000)

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
            time.sleep(0.5)
            resp = requests.get(
                self.getURL(),
            )
            if resp.text.startswith(u'\ufffd'):
                events = [json.loads(event) for messageid, endpoint, event in re.findall(u'\ufffd\d+\ufffd5:(.*?):(.*?):([^\ufffd]*)', resp.text)]
            else:
                events = [json.loads(event) for messageid, endpoint, event in re.findall(u'5:(.*?):(.*?):(.*?)\s*$', resp.text)]
            for event in events:
                if event['name'] == 'chat':
                    self.on_chat(event['args'][0])
                if event['name'] == 'join':
                    self.on_join(event['args'][0])

    def __init__(self, url, port, maxurl, maxport, username, conversation):
        #print 'Opening Messenger as %s on conversation %s' % (username, conversation)
        self.url = url
        self.port = port
        self.schema = 'https' if self.port == 443 else 'http'

        self.maxurl = maxurl
        self.maxport = maxport
        self.maxschema = 'https' if self.maxport == 443 else 'http'

        self.username = username
        self.conversation = conversation

        self.sessionid = None
        resp = requests.get(self.getURL())
        self.sessionid, heartbeat, timeout, transports = resp.text.split(':')
        self.heartbeat_timeout = int(heartbeat)
        self.timeout = int(timeout)
        self.transports = transports.split(',')

        #Connect to namespace
        resp = requests.post(self.getURL(), data='1::/max')
        if resp.status_code != 200:
            print 'connect', resp.status_code

        #Join conversation
        requests.post(self.getURL(), data='5::/max:{"name":"join","args":["%s"]}' % self.username)
        if resp.status_code != 200:
            print 'connect', resp.status_code

        self.setHeaders()
        self.total_received = 0
        self.total_elapsed = 0
        self.joined = 1

        gevent.spawn(self.eventListener)
        gevent.spawn(self.heartbeat)

    def on_chat(self, *args):
        now = datetime.now()
        emited = datetime.strptime(args[0]['emited'], "%Y-%m-%dT%H:%M:%S.%f")
        elapsed = now - emited

        self.total_elapsed += elapsed.total_seconds()
        self.total_received += 1

        #print 'Received message from %s (%.4f seconds)' % (args[0]['from'], self.total_elapsed)
        #self.sendMessage('Hola')

    def on_join(self, *args):
        print args
        self.joined = args[0]['inroom']
        #print '%s joined user %s on the conversation (%d)' % (args[0]['username'], self.username, self.joined)

    def setHeaders(self):
        self.headers = {
            'X-Oauth-Token': '54601948560149560',
            'X-Oauth-Username': self.username,
            'X-Oauth-Scope': 'widgetcli',
        }

    def notify(self, stime, r, **kwargs):
        #print '%s sent' % self.username
        chatargs = {'conversation': self.conversation, 'emited': stime, 'from': self.username}
        requests.post(self.getURL(), data='5::/max:{"name":"chat","args":[%s]}' % json.dumps(chatargs))

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
        requests.post(
            '{}://{}:{}/conversations/{}/messages'.format(self.maxschema, self.maxurl, self.maxport, self.conversation),
            data=json.dumps(payload),
            headers=self.headers,
            hooks=dict(response=callback)
        )


# class WebsocketMessenger(object):

#     def connect_1(self):
#         try:
#             return SocketIO(self.url, self.port)
#         except:
#             return False

#     def connect_2(self):
#         try:
#             return self.socket.connect('/max')
#         except:
#             return False

#     def timestamp(self):
#         return int(float(datetime.now().strftime('%s.%f')) * 1000)

#     def __init__(self, url, port, maxurl, maxport, username, conversation):
#         #print 'Opening Messenger as %s on conversation %s' % (username, conversation)
#         self.url = url
#         self.port = port
#         self.schema = 'https' if self.port == 443 else 'http'

#         self.maxurl = maxurl
#         self.maxport = maxport
#         self.maxschema = 'https' if self.maxport == 443 else 'http'
#         self.username = username
#         self.conversation = conversation
#         self.socket = False
#         # count = 1
#         # while self.socket is False and count < 5:
#         #     self.socket = self.connect_1()
#         #     #gevent.sleep(0.1)
#         #     print 'try connect 1 %d' % count
#         #     count += 1
#         if self.socket is False:
#             self.socket = SocketIO(self.url, self.port)
#         self.chat = False

#         # count = 1
#         # while self.chat is False and count < 5:
#         #     self.chat = self.connect_2()
#         #     #gevent.sleep(0.1)
#         #     print 'try connect 2 %d' % count
#         #     count += 1
#         if self.chat is False:
#             self.chat = self.socket.connect('/max')
#         # self.chat.on('message', self.on_message)
#         self.chat.on('listening', self.on_listening)
#         self.chat.on('joined', self.on_joined)
#         self.chat.on('people', self.on_people)
#         self.chat.on('update', self.on_update)
#         self.chat.emit('join', {'username': self.username, 'timestamp': self.timestamp()})
#         self.setHeaders()
#         self.total_received = 0
#         self.total_elapsed = 0
#         self.joined = 1

#     def on_people(self, *args):
#         #print '%d in room' % args[0]['inroom']
#         self.joined = args[0]['inroom']

#     def on_joined(self, *args):
#         #print '%s joined %s in conversation %s' % (args[0]['username'], self.username, args[0]['conversation'])
#         pass

#     def on_listening(self, *args):
#         #print '%s is listening on conversations %s' % (self.username, args[0]['conversations'])
#         pass

#     # def on_message(self, *args):
#     #     now = datetime.now()
#     #     emited = datetime.strptime(args[0]['timestamp'], "%Y-%m-%dT%H:%M:%S.%f")
#     #     elapsed = now - emited

#     #     self.total_elapsed += elapsed.total_seconds()
#     #     self.total_received += 1

#     #     #print 'Received message from %s (%.4f seconds)' % (args[0]['username'], self.total_elapsed)

#     def on_update(self, *args):
#         #print 'New message on conversation from %s, %s refreshes' % (args[0]['username'], self.username)
#         now = datetime.now()
#         emited = datetime.strptime(args[0]['timestamp'], "%Y-%m-%dT%H:%M:%S.%f")
#         elapsed = now - emited

#         self.total_elapsed += elapsed.total_seconds()
#         self.total_received += 1

#         pass

#     def setHeaders(self):
#         self.headers = {
#             'X-Oauth-Token': '54601948560149560',
#             'X-Oauth-Username': self.username,
#             'X-Oauth-Scope': 'widgetcli',
#         }

#     def notify(self, stime, r, **kwargs):
#         #print '%s sent' % self.username
#         self.chat.emit('message', {'conversation': self.conversation, 'timestamp': stime})

#     def sendMessage(self, message):
#         payload = {
#             "object": {
#             "objectType": "note",
#             "content": message
#             }
#         }
#         from functools import partial
#         req_start = datetime.now().isoformat()
#         callback = partial(self.notify, req_start)
#         self.notify(req_start, None)

#         # requests.post(
#         #     '{}://{}:{}/conversations/{}/messages'.format(self.maxschema, self.maxurl, self.maxport, self.conversation),
#         #     data=json.dumps(payload),
#         #     headers=self.headers,
#         #     hooks=dict(response=callback)
#         # )


HOST = 'localhost'
PORT = '8080'

MAXTALK_HOST = 'localhost'
MAXTALK_PORT = '6545'

SCHEMA = 'https' if PORT == 443 else 'http'
MAX_URL = '{}://{}:{}'.format(SCHEMA, HOST, PORT)
MAXUI_DEV_VISUAL_DEBUG_USER = 'usuari.iescude'

ADMIN_HEADERS = {
    'X-Oauth-Token': '54601948560149560',
    'X-Oauth-Username': 'carles.bruguera',
    'X-Oauth-Scope': 'widgetcli',
}


def createUsers(g, num):
    sys.stdout.write("Creating %d users " % num)
    sys.stdout.flush()
    users = []
    for i in range(num):
        username = 'maxtalk-testuser-%d_%d' % (g, i + 1)
        requests.post(
            '{}/people/{}'.format(MAX_URL, username),
            data=json.dumps({}),
            headers=ADMIN_HEADERS,
        )
        sys.stdout.write(".")
        sys.stdout.flush()

        users.append(username)
    print
    return users


def createConversation(users):
    headers = dict(ADMIN_HEADERS)
    headers['X-Oauth-Username'] = users[0]

    payload = {
        "contexts": [
            {
                "objectType": "conversation",
                "participants": users,

            }
        ],
        "object": {
            "objectType": "note",
            "content": "Init"
        }
    }
    req = requests.post(
        '{}/conversations'.format(MAX_URL),
        data=json.dumps(payload),
        headers=headers,
    )
    return json.loads(req.text)['contexts'][0]['id']


def start_messenger(username, conversation, tid, userid):
    t0 = datetime.now()
    messenger = WebsocketMessenger(MAXTALK_HOST, MAXTALK_PORT, HOST, PORT, username, conversation)
    #messenger = LongpollingMessenger(MAXTALK_HOST, MAXTALK_PORT, HOST, PORT, username, conversation)
    t1 = datetime.now()
    sec = t1 - t0
    messenger.join_time = sec.total_seconds()
    #wait for others messengers to start listening
    #print '[%d] Waiting other users to join' % tid
    while messenger.joined < USERS:
        gevent.sleep(0.1)
    print '[%d] Everybody In, starts talking' % tid

    # #user-order based wait to simulate a human rate
    # #gevent.sleep(userid * RATE)
    for i in range(MESSAGES):
         messenger.sendMessage("I'm %s" % username)
         gevent.sleep(WAIT)
    while messenger.total_received < ((USERS * MESSAGES) - MESSAGES):
    #     #print messenger.total_received
         gevent.sleep(1)
    #     #print 'waiting to receive remaining messages'
    #print '[%d] elapsed %d, received%d' % (tid, messenger.total_elapsed, messenger.total_received)
    messenger.seconds_per_message = messenger.total_elapsed / messenger.total_received
    print '[%d] Received %d messages in %.4f seconds (~%.4f seconds/message)' % (tid, messenger.total_received, messenger.total_elapsed, messenger.total_elapsed / messenger.total_received)
    gevent.sleep(1)
    return messenger


GROUPS = 1
USERS = 20
MESSAGES = 5
RATE = 1  # Messages per second in a conversation
#WAIT = RATE * USERS
WAIT = RATE

if __name__ == '__main__':

    #Enable script stop by CTRL + C
    gevent.signal(signal.SIGQUIT, gevent.shutdown)

    groups = []
    messenger_threads = []

    conversations = {}

    print "Setup users and conversations"
    for g in range(GROUPS):
        print 'Conversation %d' % (g + 1)
        print
        # Create test users in a conversation
        users = createUsers(g, USERS)
        #users.append(MAXUI_DEV_VISUAL_DEBUG_USER)
        conversation_id = createConversation(users)
        print 'Created conversation %s' % conversation_id
        print '-' * 80
        conversations[conversation_id] = users
    print
    print '*' * 40
    print "Spawning %d threads " % (GROUPS * USERS)
    print '*' * 40
    print

    #Spawn a messenger for each user in the conversations
    for sec, g in enumerate(conversations.items()):
        cid, users = g
        for num, user in enumerate(users):
            messenger_threads.append(gevent.spawn(start_messenger, user, cid, (sec * 20) + (num + 1), num))
    gevent.joinall(messenger_threads)
    times = [a.value.join_time for a in messenger_threads]

    print
    print
    print 'RESULTS'
    print '------------------'
    print
    print 'CONVERSATIONS: %d' % GROUPS
    print 'USERS / CONVERSATION: %d' % USERS
    print 'TOTAL USERS: %d ' % (USERS * GROUPS)
    print
    print 'CONNECT TIMINGS'
    print '------------------'
    print 'AVERAGE', sum(times) / len(messenger_threads)
    print 'MIN ', min(times)
    print 'MAX ', max(times)
    print
    message_times = [a.value.seconds_per_message for a in messenger_threads]
    print 'MESSAGE TIMINGS'
    print '------------------'
    print 'AVERAGE', sum(message_times) / len(messenger_threads)
    print 'MIN ', min(message_times)
    print 'MAX ', max(message_times)
    print

