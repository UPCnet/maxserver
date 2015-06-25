Setup a development max server (With local oauth)
=================================================

This buildout setups all components needed for a full stack max deployment. An existing oauth server is assumed to exist somewhere. Later on this document is explained where to setup the location of this server.

..note:: All usernames referenced on this document MUST exist on the storage system that is linked to the choosen oauth server. (i.e. an LDAP server)

Configuration steps
-------------------

- Bootstrap and buildout::

    python bootstrap.py -c devel-with-osiris.cfg

The generated customizeme.cfg file has sensible defaults for a development environment, that you're welcome to modify to suit your needs. One of the thing you may want to modify is to enable ssl in devel deployment. See the - `Enabling ssl <ssl.rst>`_ section to enable ssl for a development instance, prior to execute next steps on this guide.

Another thing you may want to modify is changing the default oauth server, and point to another one::

    [hosts]
    oauth = your.oauth.com

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


