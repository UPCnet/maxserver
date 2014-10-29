Setup a bigmax server
=========================

A server with different max instances will have one bigmax server.

    cd /var/
    git clone git@github.com:UPCnet/maxserver bigmax
    cd /var/bigmax
    /var/python/python2.7/bin/python bootstrap.py -c bigmax-only.cfg

Edit customizeme.cfg and modify the following options, each in its correct section. The port index must 0, in this server is only used to generate circus ports

    [hosts]
    main = {server_dns},

    [urls]
    oauth = {oauth_url}

    [max-config]
    name = {instance_name}

    [ports]
    port_index = 0

    [urls]
    oauth = {oauth_url}
    rabbit = amqp://admin:{rabbitmq_password}@{rabbit_server}:5672/%2F

Set the correct type of oauth server only if you are **NOT** a osiris server::

    [max-config]
    use_osiris = false

then proceed to execute buildout::

    ./bin/buildout -c max-only.cfg


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
