Setup a uTalk server
====================

Create utalk server instanceetup steps on each server::

    cd /var
    git clone git@github.com:UPCnet/maxserver utalk
    cd /var/{server_dns}
    /var/python/python2.7/bin/python bootstrap.py -c talk-only.cfg

Configure customizeme.cfg modifying the following options::

    [maxbunny-config]
    default_domain = {domain_name}

    [hosts]
    main = {rabbit_server}
    rabbit-main = {server_hostname}

    [urls]
    max = {max_server_base_url}
    oauth = {oauth_server_base_url}

Execute buildout::

    ./bin/buildout -c talk-only.cfg

Create init script for the mongodb instance, at ``/etc/init.d/mongodb``. Use this snippet as a template::

#!/bin/sh
### BEGIN INIT INFO
# Provides:          Utalk Server
# Required-Start:    $remote_fs $syslog $network
# Required-Stop:     $remote_fs $syslog $network
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start daemon at boot time
# Description:       Enable service provided by daemon.
### END INIT INFO

    WORKDIR=/var/{server_dns}
    CONFDIR=$WORKDIR/config
    ENDPOINT=14101

    case "$1" in
    'start')
            $WORKDIR/bin/circusd $CONFDIR/circus.ini --daemon
    ;;
    'stop')
            $WORKDIR/bin/circusctl --endpoint tcp://127.0.0.1:$ENDPOINT stop
            $WORKDIR/bin/circusctl --endpoint tcp://127.0.0.1:$ENDPOINT quit
    ;;
    'restart')
            $WORKDIR/bin/circusctl --endpoint tcp://127.0.0.1:$ENDPOINT restart
    ;;
    *)
        echo "Usage: /etc/init.d/utalk { start | stop | restart }"
        ;;
    esac
    exit 0


Setup init script and start utalk server instance::

    chmod +x /etc/init.d/utalk
    update-rc.d utalk defaults
    /etc/init.d/utalk start

Run once ``/bin/rabbitmqctl list_users`` to generate cookie file and restart. After this you can create a admin user and set its permissions::

    ./bin/rabbitmqctl add_user admin nbyLidT8
    ./bin/rabbitmqctl set_user_tags admin administrator
    ./bin/rabbitmqctl set_permissions -p "/" admin ".*" ".*" ".*"


Enabling twitter service
------------------------




* First you have to create a config/instances.ini file, you can use config/templates/instances.ini.template to copy from. The section name [max_xxxxxx], where xxxxx indicates the value of name in the [max] section of the buildout. can be repeated N times, one for each max that Tweety will be listening tweets for. If in development,  you can leave max_default as the only one.

Also there is a script namped bin/max.newinstance that will guide you in the process of creating each instance
