Setup a max server
=========================

A server can hold several max server instances. We will centralize all instances in a known folder with the server name ``{server_dns}``. Use server domain name for this variable. Each instance will have the same name, that will be used trough all the process::

    cd /var/{server_dns}
    git clone git@github.com:UPCnet/maxserver {instance_name}
    cd /var/{server_dns}/{instance_name}
    /var/python/python2.7/bin/python bootstrap.py -c max-only.cfg

Edit ``/var/{server_dns}/{instance_name}/mongoauth.cfg`` and fill in the password for the admin user of cluster in use.

Edit customizeme.cfg and modify the following options, each in its correct section. The port index must be a number, starting at 1, that will be added to 10000 to calculate the real port. Each instance must have a different port_index::

    [hosts]
    main = {server_dns},
    rabbitmq = {rabbit_server},
    mongodb_cluster = cluster1:27017,cluster2:27017,cluster3:27017

    [max-config]
    name = {instance_name}

    [ports]
    port_index =  {port_index}

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

    WORKDIR=/var/{server_dns}/{instance_name}
    CONFDIR=$WORKDIR/config
    ENDPOINT={circus_endpoint}

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
    echo "Usage: $0 { start | stop | restart }"
    ;;
    esac
    exit 0

Create nginx entry for max at ``/var/nginx/config/max-instances/{instance_name}.conf``, by using this snippet as a template. ``{max_port}`` must be 1000 plus the ``{port_index}`` choosed::::

    location = /{instance_name} {rewrite ^([^.]*[^/])$ $1/ permanent;}

    location ~* ^/{instance_name}/stomp {
        proxy_set_header X-Virtual-Host-URI $scheme://max.upcnet.es/{instance_name};
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        rewrite ^/{instance_name}/(.*) /$1 break;
        proxy_pass    http://rabbitmq_web_stomp_server;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
     }

    location ~* ^/{instance_name}/(?!contexts|people|activities|conversations|messages|admin|info).*$ {
        proxy_set_header X-Virtual-Host-URI $scheme://max.upcnet.es;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        rewrite ^/{instance_name}/(.*) /{instance_name}/$1 break;

        proxy_pass    http://max.upcnet.es:11000;
     }

    location ~ ^/{instance_name}/(.*) {

        if ($request_method = 'OPTIONS') {

            # Tell client that this pre-flight info is valid for 20 days
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain charset=UTF-8';
            add_header 'Content-Length' 0;

            return 200;
        }

        proxy_set_header X-Virtual-Host-URI $scheme://max.upcnet.es/{instance_name};
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        rewrite ^/{instance_name}/(.*) /$1 break;

        proxy_pass   http://max.upcnet.es:{max_port};
    }

Create circus entry for max at ``/var/nginx/config/circus-instances/{instance_name}.conf``, by using this snippet as a template. ``{circus_nginx_port}`` must be 15000 plus the ``{port_index}`` choosed::

    server {
       listen   {circus_nginx_port};
       server_name  localhost;

       location / {

             proxy_http_version 1.1;
             proxy_set_header Upgrade $http_upgrade;
             proxy_set_header Connection "upgrade";
             proxy_set_header Host $host:$server_port;
             proxy_set_header X-Real-IP $remote_addr;
             proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
             proxy_set_header X-Forwarded-Proto http;
             proxy_set_header X-Forwarded-Host $host:$server_port;
             proxy_pass http://localhost:{circus_httpd_endpoint};
             auth_basic            "Restricted";
             auth_basic_user_file  /var/nginx/config/circus.htpasswd;
        }
    }

Setup init script and start max instance::

    chmod +x /etc/init.d/max_{instance_name}
    update-rc.d max_{instance_name} defaults
    /etc/init.d/max{instance_name} start
