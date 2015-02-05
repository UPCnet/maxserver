Setup a development max server
==============================

- Bootstrap and buildout::

    python bootstrap.py -c devel.cfg

The generated customizeme.cfg file has sensible defaults for a develompent environment, that you're welcome to modify to suit your needs. One of the thing you may want to modify is to enable ssl in devel deployment. See the - `Enabling ssl <ssl.rst>`_ section to enable ssl for a development instance, prior to execute next steps on this guide.

- Execute buildout::

    ./bin/buildout -c devel.cfg


- Start supervisor::

    ./bin/supervisord

- By default the database will be initialized with permissions for a user named "restricted". If you want other users to be set as initial administators, add them on file ``config/.authorized_users`` . In both cases, create the initial persistent security setting by executing ::

    ./bin/initialize_max_db config/max.ini

* A file placed in ``config/cloudapis.ini``, waits for you to fill in the twitter settings for your twitter user. If you don't plan to enable twitter service on this max server, you can skip this step. Once filled, execute the following command::

    ./bin/max.cloudapis -c config/common.ini -a config/cloudapis.ini

.. note:: This file is not included with the repo's files, is created by the boostraping script. So don't be afraid, that your twitter config won't go anywhere!.

* Initialize max.ui development widget base settings, it will ask for your credentials
  and store them in .max_settings::

    ./bin/maxui.setup

* Add the ``restricted`` user and any users you want/need to max. You'll be asked a username and password the first time. Use "restricted" or any of the users you previosly put in ``config/.authorized_users``::

    ./bin/max.devel add user restricted

* Initialize all the needed for RabbitMQ to work with max. This will create all the exchanges and queues nedded for each user that exists on the database, along with all the common ones::

.. note:: You can run this command every time you want to ensure consistency of the current rabbit exchanges and queues, related with users and conversations present on max::

    ./bin/max.rabbit -c config/max.ini

* Restart max process to reload all the changes::

    $ ./bin/supervisorctl restart max

