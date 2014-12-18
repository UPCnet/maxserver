Setup a max nginx server
=========================

The max nxing server configuration is designed to serve several things to diffent destinations:

Steps to be done in the same machine where max instances are located::

    cd /var
    git clone git@github.com:UPCnet/maxserver nginx
    cd /var/nginx
    /var/python/python2.7/bin/python bootstrap.py -c nginx-only.cfg

Edit customizeme.cfg and modify the followig options, each in its correct section::

    [hosts]
    main = server.name.com
    rabbitmq = rabbitserver.name.com

    [ports]
    nginx = 443
    bigmax = 11001

    [nginx-config]
    certificate = /path/to/certificate
    certificate-key = /path/to/certificate-priv-key

then proceed to execute buildout::

    ./bin/buildout -c nginx-only.cfg

Create init script for the nginx instance, at ``/etc/init.d/nginx``. Use this snippet as a template::

        #!/bin/sh
        ### BEGIN INIT INFO
        # Provides:       nginx
        # Required-Start:    $local_fs $remote_fs $network $syslog $named
        # Required-Stop:     $local_fs $remote_fs $network $syslog $named
        # Default-Start:     2 3 4 5
        # Default-Stop:      0 1 6
        # Short-Description: starts the nginx web server
        # Description:       starts nginx using start-stop-daemon
        ### END INIT INFO

        PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
        DAEMON=/var/nginx/parts/nginx/sbin/nginx
        DAEMON_OPTS="-c /var/nginx/config/nginx.conf"
        NAME=nginx
        DESC="MAX servers"

        # Include nginx defaults if available
        if [ -f /etc/default/nginx ]; then
             . /etc/default/nginx
        fi

        test -x $DAEMON || exit 0

        set -e

        . /lib/lsb/init-functions


        PID=$(awk -F'[ ;]' '/[^#]pid/ {print $2}' /etc/nginx/nginx.conf)
        if [ -z "$PID" ]
        then
          PID=/run/nginx.pid
        fi


        # Check if the ULIMIT is set in /etc/default/nginx
        if [ -n "$ULIMIT" ]; then
          # Set the ulimits
          ulimit $ULIMIT
        fi


        test_nginx_config() {
                  $DAEMON -t $DAEMON_OPTS >/dev/null 2>&1
                  retvar=$?
                  if [ $retvar -ne 0 ]
                  then
                       exit $retvar
                  fi
        }


        start() {
                  start-stop-daemon --start --quiet --pidfile $PID \
                       --retry 5 --exec $DAEMON --oknodo -- $DAEMON_OPTS
        }


        stop() {
                  start-stop-daemon --stop --quiet --pidfile $PID \
                       --retry 5 --oknodo --exec $DAEMON
        }


        case "$1" in
             start)
                  test_nginx_config
                  log_daemon_msg "Starting $DESC" "$NAME"
                  start
                  log_end_msg $?
                  ;;


             stop)
                  log_daemon_msg "Stopping $DESC" "$NAME"
                  stop
                  log_end_msg $?
                  ;;


             restart|force-reload)
                  test_nginx_config
                  log_daemon_msg "Restarting $DESC" "$NAME"
                  stop
                  sleep 1
                  start
                  log_end_msg $?
                  ;;


             reload)
                  test_nginx_config
                  log_daemon_msg "Reloading $DESC configuration" "$NAME"
                  start-stop-daemon --stop --signal HUP --quiet --pidfile $PID \
                       --oknodo --exec $DAEMON
                  log_end_msg $?
                  ;;


             configtest|testconfig)
                  log_daemon_msg "Testing $DESC configuration"
                  if test_nginx_config; then
                       log_daemon_msg "$NAME"
                  else
                       exit $?
                  fi
                  log_end_msg $?
                  ;;


             status)
                  status_of_proc -p $PID "$DAEMON" nginx
                  ;;


             *)
                  echo "Usage: $NAME {start|stop|restart|reload|force-reload|status|configtest}" >&2
                  exit 1
                  ;;
        esac


        exit 0


Create a password file for a user named admin to be used by circus instances::

    htpasswd -c /var/nginx/config/circus.htpasswd

Setup init script and start nginx instance::

    chown -R pyramid.pyramid /var/nginx
    ln -s /var/nginx/config /etc/nginx
    chmod +x /etc/init.d/nginx
    update-rc.d nginx defaults
    /etc/init.d/nginx start
