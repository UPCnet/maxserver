import sys
import requests
import json
import os
import signal

from datetime import datetime

import gevent
from gevent.queue import Queue
from gevent.event import AsyncResult

from gevent.monkey import patch_all

from messengers import PollingMessenger
from messengers import WebsocketMessenger


patch_all()


def createUsers(g, num):
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
#MAXTALK_HOST = 'rocalcom.upc.edu'
#MAXTALK_PORT = 443
MAXTALK_HOST = 'localhost'
MAXTALK_PORT = 6545

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
MESSAGES = 10
RATE = 1  # Messages per second in a conversation
#WAIT = RATE * USERS
WAIT = RATE


# declare events
start_talking = AsyncResult()
all_messages_received = AsyncResult()


def start_messenger(username, conversation, tid, userid, mtype, everybody, logger):
    t0 = datetime.now()
    if mtype == 'xhr-polling':
        Messenger = PollingMessenger
    elif mtype == 'websocket':
        Messenger = WebsocketMessenger

    messenger = Messenger(MAXTALK_HOST, MAXTALK_PORT, HOST, PORT, username, conversation, everybody, logger)

    # Store the elapsed connection time
    t1 = datetime.now()
    sec = t1 - t0
    messenger.join_time = sec.total_seconds()

    def start():
        start_talking.get()

    if userid == 1:
        def asker(messenger):
            while messenger.joined < USERS:
                gevent.sleep(10)
                messenger.emit('ask', messenger.conversation)

        gevent.spawn(asker, messenger)

    start_talking.get()

    # gevent.joinall([
    #     gevent.spawn(start),
    # ])

    messenger.start_talking_time = datetime.now()
    # # #user-order based wait to simulate a human rate
    # # #gevent.sleep(userid * RATE)

    for i in range(MESSAGES):
        messenger.sendMessage("I'm %s" % username)
        gevent.sleep(WAIT)
    #print 'done', username
    all_messages_received.get()
    # while messenger.total_received < ((USERS * MESSAGES) - MESSAGES):
    #     gevent.sleep(0.1)

    messenger.end_talking_time = datetime.now()
    messenger.seconds_per_message = messenger.total_elapsed / messenger.total_received
    gevent.sleep(1)
    return messenger

if __name__ == '__main__':

    #Enable script stop by CTRL + C
    gevent.signal(signal.SIGQUIT, gevent.shutdown)
    everybody = Queue()
    message_queue = Queue()

    def waiter(conversations):
        while sum(conversations.values()) < (GROUPS * USERS):
            convs = everybody.get()
            for key, value in convs.items():
                if key in conversations.keys():
                    if value > conversations[key]:
                        conversations[key] = value
            os.system('clear')
            print
            print '============================================'
            print ' Wating for all users to join conversations'
            print '============================================'
            print
            print '\n'.join([' * %s: %d' % (key, value) for key, value in conversations.items()])
            gevent.sleep(0)
        print
        print ' %d users joined on %d conversations, Everyone In.' % (GROUPS * USERS, GROUPS)
        print ' Start talking . . .'
        print
        start_talking.set()

    def message_log():
        received = 0
        total_notifications = USERS * MESSAGES * (USERS - 1) * GROUPS
        while received < total_notifications:
            message_queue.get()
            received += 1
            sys.stdout.write('\r %d / %d received' % (received, total_notifications))
            sys.stdout.flush()
            gevent.sleep(0)

        all_messages_received.set()

    groups = []
    messenger_threads = []
    conversations = {}

    os.system('clear')

    print
    print '==============================='
    print " Setup users and conversations"
    print '==============================='
    print
    for g in range(GROUPS):
        sys.stdout.write(' Creating conversation %d with %d users:' % ((g + 1), USERS))
        sys.stdout.flush()
        # Create test users in a conversation
        users = createUsers(g, USERS)
        #users.append(MAXUI_DEV_VISUAL_DEBUG_USER)
        conversation_id = createConversation(users)
        print ' %s DONE.' % conversation_id
        conversations[conversation_id] = users
    gevent.sleep(0.5)
    os.system('clear')
    print
    print '======================='
    print " Spawning %d threads " % (GROUPS * USERS)
    print '======================='
    print

    gevent.spawn(waiter, dict([(key, 0) for key, value in conversations.items()]))
    gevent.spawn(message_log)

    gevent.sleep(0.5)
    #Spawn a messenger for each user in the conversations
    for sec, g in enumerate(conversations.items()):
        cid, users = g
        for num, user in enumerate(users):
            messenger_threads.append(gevent.spawn(start_messenger, user, cid, (sec * 20) + (num + 1), num, MESSENGER_TYPE, everybody, message_queue))
    gevent.joinall(messenger_threads)

    # Collect information harvested by each thread
    connect_times = [a.value.join_time for a in messenger_threads]
    message_times = [a.value.seconds_per_message for a in messenger_threads]

    first_message_time = min([a.value.start_talking_time for a in messenger_threads])
    last_message_time = min([a.value.end_talking_time for a in messenger_threads])
    total_sending_time = last_message_time - first_message_time
    total_sending_time = total_sending_time.total_seconds()

    print
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

    print 'Message notification times'
    print '------------------------------------'
    print ' AVERAGE : %.2f seconds/message' % (sum(message_times) / len(messenger_threads))
    print ' MIN     : %.2f seconds/message' % (min(message_times))
    print ' MAX     : %.2f seconds/message' % (max(message_times))
    print
    print 'TOTAL sending time : %.2f (%.3f / message)' % (total_sending_time, total_sending_time / (USERS * GROUPS * MESSAGES))
    print
    print
