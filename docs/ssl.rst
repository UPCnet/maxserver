Enabling ssl on a development environment
=========================================

To enable ssl there are serveral settings you need to modify in customize.cfg:

    TODO: list of settings to modify

    port 443
    http --> https

    certificates variables point to ssl/localhost.*

And also you'll need to generate a ``dhparam.pem`` file for this server with the following command:

    openssl dhparam -out config/ssl/dhparam.pem 2048

