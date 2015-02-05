TODO



* customizeme.cfg:

hostname = must match hostname seen with hostname command on terminal


* guest user is only allowes locahost, so create an admin user and grant permissions

env HOME=/var/pyramid/max/var/rabbitmq/home/ ./bin/rabbitmqctl -n rabbit@rocalcom add_user admin spdLidT8
./bin

env HOME=/var/pyramid/max/var/rabbitmq/home/ ./bin/rabbitmqctl -n rabbit@rocalcom set_user_tags admin administrator

env HOME=/var/pyramid/max/var/rabbitmq/home/ ./bin/rabbitmqctl -n rabbit@rocalcom set_permissions -p / admin ".*" ".*" ".*"
