#!/usr/bin/env python

from __future__ import print_function


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
            date = datetime.datetime.strptime(
                re.sub(r'\s\(\w+\)$', '', date),
                "%a, %d %b %Y %H:%M:%S %z")
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
