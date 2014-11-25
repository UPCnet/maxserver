Setup a supervisor process
==========================

A server with different pieces deployed will need a supervisor to controll them all. Each piece will generate its own supervidor configurations, and this buildout will create a unique instance with all the merged supevirsors config files.

    cd /var/
    git clone git@github.com:UPCnet/maxserver supervisor
    cd /var/supervisor
    /var/python/python2.7/bin/python bootstrap.py -c supervisor-only.cfg

Edit customizeme.cfg and modify the following options, each in its correct section. The parts section should be a list of supervisor configurations to be merged. If not present or empty, a serch will be made starting 2 folders avobe, and looking for files named supervisord.conf

    [supervidor]
    user = {supervisor_username}
    password = {supervisor_password}
    parts = /foo/bar
            /bar/baz

    [ports]
    supervisor = {supervisor_port}


    ./bin/buildout -c supervisor-only.cfg


Create init script for the max instance, at ``/etc/init.d/max_{instance_name}``. Use this snippet as a template. Circus port must be 14100 plus the ``{port_index}`` choosed::

    #!/bin/sh
    # chkconfig: - 85 15
    # description: Bigmax app

    WORKDIR=/var/bigmax
    CONFDIR=$WORKDIR/config
    ENDPOINT=14100

    case "$1" in
    'start')
            $WORKDIR/bin/circusd $CONFDIR/circus.ini --daemon
    ;;
    'stop')
            $WORKDIR/bin/circusctl --endpoint tcp://127.0.0.1:$ENDPOINT stop
            sleep 5
            $WORKDIR/bin/circusctl --endpoint tcp://127.0.0.1:$ENDPOINT quit
    ;;
    'restart')
            $WORKDIR/bin/circusctl --endpoint tcp://127.0.0.1:$ENDPOINT restart
    ;;
    *)
        echo "Usage: /etc/init.d/bigmax { start | stop | restart }"
        ;;
    esac
    exit 0


Setup init script and start max instance::

    chmod +x /etc/init.d/bigmax
    update-rc.d bigmax defaults
    /etc/init.d/bigmax start
