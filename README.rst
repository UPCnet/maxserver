Maxserver buildout Development edition
======================================


Steps to succesfully deploy a max locally
-----------------------------------------

* Install OS library dependencies (for Ubuntu systems)::

    apt-get install zlib1g-dev build-essential libldap2-dev libsasl2-dev
    libreadline6-dev libncurses5-dev libncursesw5-dev libsqlite3-dev libssl-dev
    tk-dev libgdbm-dev libc6-dev libbz2-dev libxslt1-dev libpcre3-dev

* Install OSX dependencies::

    brew install pcre

* Bootstrap and execute buildout::

    $ python bootstrap.py
    $ ./bin/buildout
 
* Start supervisor::

    $ ./bin/supervisord

* Create initial security settings::

    $ ./bin/initialize_max_db config/max.ini
    Created default security info in MAXDB.\n"
    Remember to restart max process!

* Create initial cloudapis settings::

    $ ./bin/max.cloudapis -c twitter.cfg
    Created cloudapis info in MAXDB.\n"
    Remember to restart max process!

* Restart max process to apply the new security settings::

    $ ./bin/supervisorctl restart max

* Initialize max.ui development widget base settings, it will ask for your credentials
  and store them in .max_settings::

    $ ./bin/maxui.setup

* Add yourself to max::

    $ ./bin/maxdevel add user your.name
    Done.

Extra steps
-----------

* If you want to enable SSL, you first have to:
    - set ``enable-ssl`` variable in ``[nginx-config]`` section to ``true``
    - set ``nginx`` variable in ``[ports]`` section to ``443``
    - remove ``parts/supervisor/supervisord.conf`` and re-run buildout

* If you are setting up a SSL production environment, also:
    - set certificate file locations in ``[nginx-config]`` section
    - set ``main`` variable in ``[hosts]`` section to your domain name


Considerations using the development version widget
---------------------------------------------------

- You must have at least an user created to view and use the widget
- ``maxui.setup`` script has configured ``src/max.ui.js/presets/base.json`` with buildout-generated parameters
- After the previous setup steps, the development widget is visible at ``http://localhost:8080/maxui-dev/devel.html``
- Default preset ``timeline`` works out-of-the-box
- You can change presets appending ``?preset=presetname``
- If you want to use the ``context`` preset, you have to create a context and subscribe user(s) to it::

        $ ./bin/max.devel add context http://contexturi ContextName
        $ ./bin/max.devel add subscription user.name http://contexturi

* If you run buildout again, you have to run ``maxui.setup``script again. Any changes will be lost.


Troubleshooting
---------------

* 401 when creating the initial user:
    - Possibly you don't have permission to request a token from the designated oauth server

* Maxtalk complains: AttributeError: 'GeventSocketIOWorker' object has no attribute 'socket'
    - Possibly wrong gunicorn version, last known working 0.16.1

* Maxtalk complains: KeyError: 'socketio' // KeyError: 'wsgi.websocket'
    - Nginx HTTP upgrade misconfiguration
