Maxserver buildout Development edition
======================================


Steps to succesfully deploy a max locally
-----------------------------------------

* Install OS library dependencies (for Ubuntu systems)::

    apt-get install zlib1g-dev build-essential libldap2-dev libsasl2-dev
    libreadline6-dev libncurses5-dev libncursesw5-dev libsqlite3-dev libssl-dev
    tk-dev libgdbm-dev libc6-dev libbz2-dev libxslt1-dev libpcre3-dev libjpeg62-dev libzlcore-dev libfreetype6-dev erlang

* Install OSX dependencies::

    brew install pcre

* Check erlang version by executing ``erl -version``. You need erlang at least 5.10.2 R16B01. If you can't get it from your distribution, get the latest erlang and build it from sources following instructions from http://www.erlang.org/doc/installation_guide/INSTALL.html#Required-Utilities_Unpackingn

* Bootstrap and execute buildout::

    $ python bootstrap.py
    $ ./bin/buildout

* Start supervisor::

    $ ./bin/supervisord

* Define the users you want to set as initial administators on file ``config/.authorized_users`` and then, create initial persistent security settings::

    $ ./bin/initialize_max_db config/max.ini
    Created default security info in MAXDB.\n"
    Remember to restart max process!

* Fill the twitter settings for your twitter user in ``config/maxbunny.ini``. The section looks like::

    [twitter]
    consumer_key =
    consumer_secret =
    access_token =
    access_token_secret =

.. note::

    If you are going to run tests (and you are), remember to load the settings
    either for the dbname of the max server and the *tests* database. You can
    supply the unified maxbunny.ini file, executing it twice, each time with a different db name.

and the command line to load them into the MAX database::

    $ ./bin/max.cloudapis -c maxbunny.ini
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

* Initialize the restricted user for use of daemon scripts (Tweety and
  Push/Tweety consumers) server settings by running::

    $ ./bin/max.setrestricted -c config/max.ini

* Initialize the RabbitMQ server settings by running::

    $ ./bin/max.rabbit -c config/max.ini

this command takes a standard max config .ini as configuration settings. This is
intended to run once in a production server or as many times as needed on
development. It creates the default artifacts in RabbitMQ server and it will
also syncronize the existing conversations in the max server with the
correspondant exchanges in the RabbitMQ server.

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

Ports used by processes
-----------------------

* Command to see which ports a process is listening to::

    $ sudo netstat --numeric --numeric-hosts --all --program | grep PID


Troubleshooting
---------------

* 401 when creating the initial user:
    - Possibly you don't have permission to request a token from the designated oauth server

* Maxtalk complains: AttributeError: 'GeventSocketIOWorker' object has no attribute 'socket'
    - Possibly wrong gunicorn version, last known working 0.16.1

* Maxtalk complains: KeyError: 'socketio' // KeyError: 'wsgi.websocket'
    - Nginx HTTP upgrade misconfiguration
