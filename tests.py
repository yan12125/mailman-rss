# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
import unittest
from mailman_rss.mailman import MailmanArchive
from mailman_rss.rss import RSSWriter
import tempfile
from six import StringIO


ARCHIVE_URL = "https://mail.python.org/pipermail/mailman-developers/"


class TestMailmanArchive(unittest.TestCase):

    def test_rsswriter_stringio(self):
        archive = MailmanArchive(ARCHIVE_URL)
        f = StringIO()
        writer = RSSWriter(fp=f, max_items=1)
        writer.write(archive)

    def test_rsswriter_filename(self):
        archive = MailmanArchive(ARCHIVE_URL)
        with tempfile.NamedTemporaryFile(suffix=".rss") as f:
            writer = RSSWriter(fp=f.name, max_items=1)
            writer.write(archive)


if __name__ == "__main__":
    unittest.main()
