Setup a development max server (With local oauth)
=================================================

This buildout setups all components needed for a full stack max deployment. The difference with devel.cfg is that local oauth server (osiris) is included, which reads user from a simple crypt-htpasswd file located at config/devel-users. This file contains some test users:

    - restricted
    - user0 to user9

All of them with password "max". This is indended for development purposes to avoid depending on an ldap server. If you already have a ldap server that you can use for development, you can modify your settings later to use it.

..note:: Whether you choose local user htpasswd storage or LDAP, all usernames referenced on this document MUST exist on the choosen user storage system.

Configuration steps
-------------------

- Bootstrap and buildout::

    python bootstrap.py -c devel-with-osiris.cfg

The generated customizeme.cfg file has sensible defaults for a development environment, that you're welcome to modify to suit your needs. One of the thing you may want to modify is to enable ssl in devel deployment. See the - `Enabling ssl <ssl.rst>`_ section to enable ssl for a development instance, prior to execute next steps on this guide.
Another thing you may want to modify is connecting osiris oauth server with an existing ldap server. To do this modify the generated customizeme.cfg, locate the ``[osiris-config]`` section, and change this settings::

    [osiris-config]
    ldap_enabled = true
    who_enabled = false

- Execute buildout::

    ./bin/buildout -c devel-with-osiris.cfg

- Start supervisor::

    ./bin/supervisord

- Max needs an user to be assigned as Manager. To create and assign initial permissions, execute the following command.

    ./bin/max.security add <username>

- Add the previously created user and any users you want/need to max. You'll be asked a username and password the first time. Use any user you just granted Manager role in the previous step. You can also::

    ./bin/max.devel add user <username>

* Restart max process to reload all the changes::

    $ ./bin/supervisorctl restart max

* Initialize RabbitMQ queues, exchanges and bindings. This will create all needed bits in RabbitMQ for each user that exists on the database::

.. note:: You can run this command every time you want to ensure consistency of the current rabbit exchanges and queues, related with users and conversations present on max::

    ./bin/max.rabbit


Optional steps
---------------

* A file placed in ``config/cloudapis.ini``, waits for you to fill in the twitter settings for your twitter user. If you don't plan to enable twitter service on this max server, you can skip this step. Once filled, execute the following command::

    ./bin/max.cloudapis -c config/common.ini -a config/cloudapis.ini

.. note:: This file is not included with the repo's files, is created by the boostraping script. So don't be afraid, that your twitter config won't go anywhere!.

* Initialize max.ui development widget base settings, it will ask for your credentials the first time, and store them in .max_settings::

    ./bin/maxui.setup


