#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import hooks
from bs4 import BeautifulSoup
import cgi
import datetime
from email.header import decode_header, make_header
from email.utils import formatdate
import gzip
import io
from logging import getLogger
import mailbox
import re
import optparse
import os
import sys
import tempfile
import time

with hooks():
    from urllib.parse import urlparse
    from urllib.request import urlopen

logger = getLogger(__name__)


def get_parser():
    parser = optparse.OptionParser(
        usage="usage: %prog [options] <archive url>")
    parser.add_option("-c", "--count", default=25, type="int",
                      help="number of messages to convert to rss")
    parser.add_option("-e", "--encoding", default="ascii", type="str",
                      help="email message encoding, default ascii")
    parser.add_option("-z", "--timezone", default=0, type="int",
                      help="default timezone, default 0")
    return parser


def usage(parser):
    parser.print_help()
    sys.exit(1)


def fetch(url):
    fd = urlopen(url)

    try:
        return fd.read()
    finally:
        fd.close()


class MailmanArchive:
    def __init__(self, archive_url):
        # normalize the archive url to make sure it ends with a slash
        if archive_url[-1] != "/":
            archive_url = archive_url + "/"

        self.archive_url = archive_url
        archive = fetch(archive_url)

        self._soup = BeautifulSoup(archive, "html.parser")

    def get_title(self):
        return self._soup.html.head.title.string

    def get_month(self, url):
        data_gz = fetch(url)

        (fd, tmpfile) = tempfile.mkstemp()

        fd = os.fdopen(fd, "w+b")
        data = gzip.GzipFile(fileobj=io.BytesIO(data_gz)).read()
        fd.write(data)
        fd.close()

        mbox = mailbox.mbox(tmpfile)
        os.remove(tmpfile)

        return mbox

    def get_month_archives(self):
        ret = []

        months = self._soup.findAll("a", href=re.compile(".*txt(.gz)?"))
        for month in months:
            url = month.get("href")

            if not url.endswith(".gz"):
                url = url + ".gz"

            url = self.archive_url + url
            ret.append(url)

        return ret


def get_part_field(part, name):
    fp = io.StringIO(part)

    for line in fp.readlines():
        if line.lower().startswith(name):
            parts = line.split(":", 1)
            return parts[1].strip()


def printrss(archive, mails, fp=None, timezone=0):
    if not fp:
        fp = io.StringIO()
    print('<?xml version="1.0" encoding="UTF-8" ?>', file=fp)
    print('<rss version="2.0">', file=fp)
    print('<channel>', file=fp)
    print('<language>%s</language>' % cgi.escape('ja-JP'), file=fp)

    title = archive.get_title()
    if title:
        print('<title>%s</title>' % cgi.escape(title), file=fp)
        print('<description>%s</description>' % cgi.escape(title), file=fp)

    link = archive.archive_url
    print('<link>%s</link>' % cgi.escape(link), file=fp)

    pubdate_rendered = False

    for mail in mails:
        date = mail.get("date")
        author = mail.get("from")
        subject = mail.get("subject")
        guid = mail.get("message-id")

        if not pubdate_rendered:
            if date:
                print('<pubDate>%s</pubDate>' % cgi.escape(date), file=fp)
            else:
                dt = datetime.datetime.now(datetime.timezone(
                    datetime.timedelta(hours=timezone)))
                print('<pubDate>%s</pubDate>' % cgi.escape(
                    formatdate(dt)), file=fp)
            pubdate_rendered = True

        print('<item>', file=fp)
        if author:
            author = author.replace(" at ", "@")
            print('<author>%s</author>' % cgi.escape(author), file=fp)

        if date:
            print('<pubDate>%s</pubDate>' % cgi.escape(date), file=fp)
            try:
                date = datetime.datetime.strptime(
                    date, "%a, %d %b %Y %H:%M:%S %z")
            except ValueError:
                date = datetime.datetime.strptime(
                    date, "%a, %d %b %Y %H:%M:%S %z (%Z)")
            date = date.astimezone(date.tzinfo)

        if subject:
            title = make_header(decode_header(cgi.escape(subject)))
            match = re.match(r'\[\w+ (\d+)\].*', str(title))
            print('<title>{}</title>'.format(title), file=fp)
            if date and match:
                link = "{}{}/{:06d}.html".format(
                    archive.archive_url, date.strftime("%Y-%B"),
                    int(match.group(1)))
                print('<link>{}</link>'.format(link), file=fp)

        if guid:
            guid = guid.strip("<>")
            print('<guid isPermaLink="false">%s</guid>' % cgi.escape(guid),
                  file=fp)

        if mail.is_multipart():
            body = mail.get_payload(0)
        else:
            body = mail.get_payload()

        parts = re.split(re.compile("^-+\s+next part\s+-+$", re.MULTILINE),
                         body)
        parts = [part.strip() for part in parts]
        body = parts[0].replace("\n", "<br/>")
        print('<description><![CDATA[%s]]></description>' % body, file=fp)

        for part in parts[1:]:
            # include enclosures
            if "A non-text attachment was scrubbed" not in part:
                continue

            mime_type = get_part_field(part, "type")
            size = get_part_field(part, "size")
            url = get_part_field(part, "url")

            if mime_type and size and url:
                o = urlparse(url)
                if o.netloc:
                    print('<enclosure url="%s" length="%s" type="%s" />' %
                          (url, size, mime_type), file=fp)

        print('</item>', file=fp)

    print('</channel>', file=fp)
    print('</rss>', file=fp)
    return fp


def main():
    parser = get_parser()
    (options, args) = parser.parse_args()

    if len(args) != 1:
        usage(parser)

    archive = MailmanArchive(args[0])
    months = archive.get_month_archives()

    if len(months) == 0:
        print("ERROR: Could not find month archives in url")
        sys.exit(1)

    mails = []

    for month_url in months:
        mbox = archive.get_month(month_url)

        if hasattr(mbox, 'get_bytes'):
            month = [mailbox.mboxMessage(
                        mbox.get_bytes(i).decode(options.encoding))
                     for i in range(len(mbox))]
        else:
            month = [mailbox.mboxMessage(
                        mbox.get_string(i).decode(
                            options.encoding).encode('utf-8'))
                     for i in range(len(mbox))]
        month.reverse()

        for mail in month:
            mails.append(mail)

        if len(mails) >= options.count:
            break

    # trim to COUNT entries
    if len(mails) > options.count:
        mails = mails[:options.count]

    printrss(archive, mails, fp=sys.stdout, timezone=options.timezone)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
