import sys
import requests
import json
from datetime import datetime

import gevent
from gevent.monkey import patch_all
import signal

from messengers import PollingMessenger
from messengers import WebsocketMessenger
patch_all()


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


HOST = 'localhost'
PORT = 8081
MAXTALK_HOST = 'localhost'
MAXTALK_PORT = 8081
SCHEMA = 'https' if PORT == 443 else 'http'
MAX_URL = '{}://{}:{}'.format(SCHEMA, HOST, PORT)
MAXUI_DEV_VISUAL_DEBUG_USER = 'usuari.iescude'
MESSENGER_TYPE = 'xhr-polling'
MESSENGER_TYPE = 'websocket'
ADMIN_HEADERS = {
    'X-Oauth-Token': '54601948560149560',
    'X-Oauth-Username': 'carles.bruguera',
    'X-Oauth-Scope': 'widgetcli',
}

GROUPS = 10
USERS = 20
MESSAGES = 20
RATE = 1  # Messages per second in a conversation
#WAIT = RATE * USERS
WAIT = RATE


def start_messenger(username, conversation, tid, userid, mtype):
    t0 = datetime.now()
    if mtype == 'xhr-polling':
        Messenger = PollingMessenger
    elif mtype == 'websocket':
        Messenger = WebsocketMessenger
    messenger = Messenger(MAXTALK_HOST, MAXTALK_PORT, HOST, PORT, username, conversation)

    # Store the elapsed connection time
    t1 = datetime.now()
    sec = t1 - t0
    messenger.join_time = sec.total_seconds()

    #wait until everyone in the conversation is in
    while messenger.joined < USERS:
        gevent.sleep(0.1)
    print '[%d] Everybody in, delivering messages' % tid

    # #user-order based wait to simulate a human rate
    # #gevent.sleep(userid * RATE)
    for i in range(MESSAGES):
        messenger.sendMessage("I'm %s" % username)
        gevent.sleep(WAIT)
    while messenger.total_received < ((USERS * MESSAGES) - MESSAGES):
        gevent.sleep(1)

    messenger.seconds_per_message = messenger.total_elapsed / messenger.total_received
    gevent.sleep(1)
    return messenger

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
    print '=' * 40
    print "       Spawning %d threads " % (GROUPS * USERS)
    print '=' * 40
    print

    #Spawn a messenger for each user in the conversations
    for sec, g in enumerate(conversations.items()):
        cid, users = g
        for num, user in enumerate(users):
            messenger_threads.append(gevent.spawn(start_messenger, user, cid, (sec * 20) + (num + 1), num, MESSENGER_TYPE))
    gevent.joinall(messenger_threads)

    # Collect information harvested by each thread
    connect_times = [a.value.join_time for a in messenger_threads]
    message_times = [a.value.seconds_per_message for a in messenger_threads]
    print
    print
    print ' RESULTS'
    print '---------'
    print
    print ' Conversations: %d' % GROUPS
    print ' Users per conversation: %d' % USERS
    print ' Total concurrent users: %d ' % (USERS * GROUPS)
    print
    print ' Time to connect to maxtalk'
    print '----------------------------'
    print ' AVERAGE : %.2f seconds' % (sum(connect_times) / len(messenger_threads))
    print ' MIN     : %.2f seconds' % (min(connect_times))
    print ' MAX     : %.2f seconds' % (max(connect_times))
    print

    print 'Message notification delivery times'
    print '------------------------------------'
    print ' AVERAGE : %.2f seconds/message' % (sum(message_times) / len(messenger_threads))
    print ' MIN     : %.2f seconds/message' % (min(message_times))
    print ' MAX     : %.2f seconds/message' % (max(message_times))
    print
