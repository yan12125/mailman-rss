# mailman-rss

A simple mailman archive -> rss converter.

## Setup

Install dependencies with `pip`.

```bash
pip install -r requirements.txt
```

## Usage


```
Usage: mailman_rss.py [options] <archive url>

Options:
  -h, --help            show this help message and exit
  -c COUNT, --count=COUNT
                        number of messages to convert to rss
  -e ENCODING, --encoding=ENCODING
                        email message encoding, default ascii
```

Example:

```bash
python mailman_rss.py http://example.com/mailman/list/
```

The script should be run from cron.

```bash
crontab -l
```

```cron
0 * * * * python mailman_rss.py http://example.com/mailman/list/ > /var/www/archive.rss
```
