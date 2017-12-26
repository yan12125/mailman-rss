mailman-rss
===========

A simple mailman archive -> rss converter. Also the command can run as a
twitter bot.

Install
-------

Install the package with ``pip``.

.. code:: bash

    pip install mailman-rss

Twitter bot can be installed with an option:

.. code:: bash

    pip install mailman-rss[twitter]

Usage
-----

::

    usage: mailman-rss [-h] [--command COMMAND] [--config CONFIG]
                       [--archive-url URL] [--max-items MAX_ITEMS] [-o OUTPUT]
                       [-l LOGLEVEL] [--encoding ENCODING] [--language LANGUAGE]

    Fetch Mailman archive and export to RSS

    optional arguments:
      -h, --help            show this help message and exit
      --command COMMAND     Command to execute, rss or twitter
      --config CONFIG       mailman-rss config json file, default None
      --archive-url URL     Archive URL to fetch
      --max-items MAX_ITEMS
                            number of messages to convert to rss
      -o OUTPUT, --output OUTPUT
                            output file name, default stdout
      -l LOGLEVEL, --loglevel LOGLEVEL
                            logging level for debugging, default warning
      --encoding ENCODING   email message encoding, default None
      --language LANGUAGE   language specification, default None

RSS Example: this will output RSS feed to stdout.

.. code:: bash

    mailman-rss --archive-url http://example.com/mailman/list/

The command can have a config file.

.. code:: bash

    mailman-rss --config /path/to/config.json

.. code:: json

    {
      "archive_url": "http://example.com/mailman/list/",
      "output": "/home/user/public_html/mailman.rss"
    }

Twitter example: twitter bot requires an application token and a storage space.
`Get Twitter API Key <https://python-twitter.readthedocs.io/en/latest/getting_started.html#getting-your-application-tokens>`_ to run the command.

.. code:: json

    {
      "command": "twitter",
      "archive_url": "http://example.com/mailman/list/",
      "db": "/home/user/scraper.sqlite3",
      "max_items": 10,
      "consumer_key": "XXXXXXXXXXXXXXXXXXXXXXXXXX",
      "consumer_secret": "XXXXXXXXXXXXXXXXXXXXXXXXXX",
      "access_token_key": "XXXXXXX-XXXXXXXXXXXXXXXXXXXXXXXXXX",
      "access_token_secret": "XXXXXXXXXXXXXXXXXXXXXXXXXX"
    }


Deploy
------

The command should be run from cron.

.. code:: bash

    crontab -l

    0 * * * * mailman-rss --archive-url http://example.com/mailman/list/ > /var/www/archive.rss
    0 * * * * mailman-rss --config /home/user/twitter-bot.json

Test
----

.. code:: bash

    tox
