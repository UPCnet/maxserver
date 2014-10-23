Setup a max mongo cluster
=========================

Mongo clusters are composed of at last 3 servers, so first of all, repeat
setup steps on each server::

    cd /var
    git clone git@github.com:UPCnet/maxserver mongodb
    cd /var/mongodb
    /var/python/python2.7/bin/python bootstrap.py -c mongodb-only.cfg

Edit customizeme.cfg and modify the followig options, each in its correct section::

    [hosts]
    main = server.name.com

    [ports]
    circus-endpoint = 28081
    circus-pubsub = 28082
    circus-stats = 28083

then proceed to execute buildout::

    ./bin/buildout -c mongodb-only.cfg

Edit the buildout-generated ``config/mongodb.conf`` and commment out the security options, to be able to
access the database the very first time::

    #security:
    #    authorization: enabled
    #    keyFile: /var/mongodb/var/mongodb-keyfile

Create init script for the mongodb instance, at ``/etc/init.d/mongodb``. Use this snipped as a template::

    #!/bin/sh
    # chkconfig: - 85 15
    # description: MongoDB Startup script

    WORKDIR=/var/mongodb
    CONFDIR=$WORKDIR/config
    ENDPOINT=28081

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
        echo "Usage: /etc/init.d/mongodb { start | stop | restart }"
        ;;
    esac
    exit 0

Setup init script and start mongodb instance::

    chmod +x /etc/init.d/mongodb
    update-rc.d mongodb defaults
    /etc/init.d/mongodb start

Setup cluster
-------------

Enter the mongo shell of one of the 3 servers and initialize it with the addresses of all the nodes.
Use the following as a template customizing the name used in ``id`` with the replicaset choosen, and
the hostname of each server::

    cd /var/mongodb
    ./bin/mongo
    rs.initialize({"_id" : "maxcluster","version" : 1,"members" : [{"_id" : 0,"host" : "host1:27017"},{"_id" : 1,"host" : "host2:27017"},{"_id" : 2,"host" : "host3:27017"}]})


A few seconds after this the shell prompt will change to show if the current node has been elected PRIMARY or is a SECONDARY NODE.

Import a remote database
-------------------------

To import a remote database, execute mongodump and mongorestore with proper host name and db name in the server that is
currently the PRIMARY::

    ./bin/mongodump --host <hostname >--db dbname -v --out dbname
    ./bin/mongorestore dbname

Data will be imported and synced across the three servers.

Enabling security
-----------------

Based on http://docs.mongodb.org/manual/tutorial/deploy-replica-set-with-auth

Excute this commands on the PRIMARY to create admin users::

    use admin
    db.createUser({
        user: "root",
        pwd: "<password-here>",
        roles: [ { role: "root", db: "admin" } ]
      });
    db.createUser( {
        user: "admin",
        pwd: "<password-here>",
        roles: [ { role: "readWriteAnyDatabase", db: "admin" } ]
      });

Shutdown all instances, and create a secure keyfile::

    openssl rand -base64 741 > var/mongodb-keyfile
    chmod 600 var/mongodb-keyfile

Replicate this file onto all cluster servers. Now you can uncomment the security options commented in the
first steps, and restart all the cluster members.

Now you can try to authentica in the mongo shell of each cluster member as follows::

    use admin
    db.auth("admin", "<password>");
