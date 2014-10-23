Enabling twitter service
------------------------

* First you have to create a config/instances.ini file, you can use config/templates/instances.ini.template to copy from. The section name [max_xxxxxx], where xxxxx indicates the value of name in the [max] section of the buildout. can be repeated N times, one for each max that Tweety will be listening tweets for. If in development,  you can leave max_default as the only one.

Also there is a script namped bin/max.newinstance that will guide you in the process of creating each instance
