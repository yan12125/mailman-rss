# -*- coding: utf-8 -*-
import argparse
import logging
import sys
from mailman_rss import MailmanArchive, RSSWriter


def parse_args():
    parser = argparse.ArgumentParser(
        prog="mailman-rss",
        description="Fetch Mailman archive and export to RSS")
    parser.add_argument("archive_url", metavar="URL",
                        help="Archive URL to fetch")
    parser.add_argument("-c", "--count", default=25, type=int,
                        help="number of messages to convert to rss")
    parser.add_argument("-o", "--output", default=None, type=str,
                        help="output file name, default stdout")
    parser.add_argument("-l", "--loglevel", default="warning",
                        help="logging level for debugging, default warning")
    parser.add_argument("--encoding", default=None, type=str,
                        help="email message encoding, default None")
    parser.add_argument("--language", default=None, type=str,
                        help="language specification, default None")
    return parser.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.loglevel.upper()),
                        stream=sys.stderr)
    archive = MailmanArchive(args.archive_url, encoding=args.encoding)
    writer = RSSWriter(fp=args.output if args.output else sys.stdout,
                       max_items=args.count,
                       language=args.language)
    writer.write(archive)


if __name__ == '__main__':
    main()
