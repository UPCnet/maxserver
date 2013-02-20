Maxserver buildout Development edition
======================================


Steps to succesfully deploy a max locally
-----------------------------------------

* Bootstrap and execute buildout, use ml-pcre.cfg on MacOS
* Start Mongo process
* Execute ./bin/initialize_max_db config/max.ini, to create initial security settings
* Add yourself as a user via a the python cli::
    ./bin/python
    >>> from maxclient import MaxClient
    >>> max = MaxClient('http://eider:8080')
    >>> max.login()
    Username: your.name
    Password: ********
    u'abcdef01234567890abcdef012345678'
    >>> max.addUser('your.name')

* Start the rest of processes


Troubleshooting
---------------

* Maxtalk complains: AttributeError: 'GeventSocketIOWorker' object has no attribute 'socket'
    - Possibly wrong gunicorn version, last known working 0.16.1

* Maxtalk complains: KeyError: 'socketio' // KeyError: 'wsgi.websocket'
    - Nginx HTTP upgrade misconfiguration
