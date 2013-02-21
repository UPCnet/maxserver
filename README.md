Maxserver buildout Development edition
======================================


Steps to succesfully deploy a max locally
-----------------------------------------

* Bootstrap and execute buildout, use ml-pcre.cfg on MacOS
* Start Mongo process
* Execute ./bin/initialize_max_db config/max.ini, to create initial security settings
* Add yourself to max,  the first time will ask for your credentials and store them in .max_settings::
    $ ./bin/maxdevel add user your.name
    New User username: carles.bruguera
    Done.

* Start the rest of processes


Considerations using the development version widget
------------------------

* You must have at least an user created to view widget
* Assuming you run the buildout with main host as "localhost":
    - You can view the development widget at http://localhost:8080/maxui-dev/devel.html
    - You can change presets with ?preset=presetname
    - Default preset ``timeline`` works out-of-the-box
    - If you want to use the ``context`` preset, you have to create a context and subscribe user(s) to it::
        $ ./bin/max.devel add context http://contexturi ContextName
        $ ./bin/max.devel add subscription user.name http://contexturi
* If you used another hostname, you have to change it in src/max.ui.js/presets/base.json


Troubleshooting
---------------

* Maxtalk complains: AttributeError: 'GeventSocketIOWorker' object has no attribute 'socket'
    - Possibly wrong gunicorn version, last known working 0.16.1

* Maxtalk complains: KeyError: 'socketio' // KeyError: 'wsgi.websocket'
    - Nginx HTTP upgrade misconfiguration
