mailman-rss
===========

A simple mailman archive -> rss converter.

Install
-------

Install the package with ``pip``.

.. code:: bash

    pip install mailman-rss

Usage
-----

::

    usage: mailman-rss [-h] [-c COUNT] [-e ENCODING] [-z TIMEZONE] [-l LOGLEVEL]
                       URL

    Fetch Mailman archive and export to RSS

    positional arguments:
      URL                   Archive URL to fetch

    optional arguments:
      -h, --help            show this help message and exit
      -c COUNT, --count COUNT
                            number of messages to convert to rss
      -e ENCODING, --encoding ENCODING
                            email message encoding, default None
      -z TIMEZONE, --timezone TIMEZONE
                            default timezone, default 0
      -l LOGLEVEL, --loglevel LOGLEVEL
                            logging level for debugging, default warning

Example:

.. code:: bash

    mailman-rss http://example.com/mailman/list/

The script should be run from cron.

.. code:: bash

    crontab -l

.. code:: cron

    0 * * * * mailman-rss http://example.com/mailman/list/ > /var/www/archive.rss

Test
----

.. code:: bash

    python tests.py
