Configuration steps
-------------------

- Bootstrap and buildout::

    python bootstrap.py --setuptools-version=38.7.0 -c devel-new.cfg --buildout-version=2.13.4

The generated customizeme.cfg file has sensible defaults for a development environment, that you're welcome to modify to suit your needs.

- Execute buildout::

    ./bin/buildout -N -c devel-new.cfg

- Start supervisor::

    ./bin/supervisord

* Restart process to reload all the changes::

    $ ./bin/supervisorctl restart process


* Run nginx, mongo and rabbit docker on your local pc and copy the demoupcnet database to mongo

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


