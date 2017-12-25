# -*- coding: utf-8 -*-
import unittest
from mailman_rss.scraper import MailmanArchive
from mailman_rss.rss import RSSWriter


ARCHIVE_URL = "https://mail.python.org/pipermail/mailman-developers/"


class TestMailmanArchive(unittest.TestCase):

    def test_archive(self):
        archive = MailmanArchive(ARCHIVE_URL)
        for index, message in enumerate(archive.iter_messages()):
            message.author
            message.subject
            message.date
            message.url
            message.stable_url
            message.body
            message.attachments()
            if index >= 2:
                break

    def test_rsswriter(self):
        archive = MailmanArchive(ARCHIVE_URL)
        writer = RSSWriter()


if __name__ == "__main__":
    unittest.main()
