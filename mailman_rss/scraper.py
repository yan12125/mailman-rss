#!/usr/bin/env python

from __future__ import print_function
from bs4 import BeautifulSoup
from logging import getLogger
import mailbox
import requests
import os
import re


logger = getLogger(__name__)


class MailmanArchive(object):
    def __init__(self, archive_url, encoding="utf-8"):
        self.encoding = encoding
        self.archive_url = archive_url
        r = requests.get(archive_url)
        self._soup = BeautifulSoup(r.text, "html.parser")

    @property
    def title(self):
        return self._soup.html.head.title.string

    def _get_month(self, url):
        r = requests.get(url, stream=True)
        with tempfile.TemporaryDirectory() as t:
            with tempfile.NamedTemporaryFile(dir=t) as f:
                f.write(gzip.GzipFile(fileobj=r.raw).read())
                return mailbox.mbox(f.name)

    def iter_mboxes(self):
        for a in self._soup.findAll("a", href=re.compile(r".*txt(.gz)?")):
            url = a.get("href")
            if not url.endswith(".gz"):
                url = url + ".gz"
            url = os.path.join(self.archive_url, url)
            yield self._get_month(url)

    def iter_messages(self):
        for mbox in self.iter_mboxes():
            for index in reversed(range(len(mbox))):
                if hasattr(mbox, "get_bytes"):
                    yield Message(
                        mbox.get_bytes(index).decode(self.encoding))
                else:
                    yield Message(
                        mbox.get_string(index).decode(self.encoding))



class Message(mailbox.mboxMessage):
    def __init__(self, *args):
        super(Message, self).__init__(*args)

    @property
    def author(self):
        value = self.get("from")
        return html.escape(value) if value else None

    @property
    def subject(self):
        value = self.get("subject")
        return make_header(decode_header(value)) if value else None

    @property
    def date(self):
        value = self.get("date")
        return dateutil.parser.parse(value) if value else None

    @property
    def message_id(self):
        return self.get("message-id")

    @property
    def parts(self):
        if self.is_multipart():
            body = self.get_payload(0)
        else:
            body = self.get_payload()
        parts = re.split(re.compile("^-+\s+next part\s+-+$", re.MULTILINE),
                         body)
        return [part.strip() for part in parts]

    @property
    def body(self):
        return self.parts[0]

    def attachments(self):
        attachments = []
        for part in self.parts[1:]:
            if "A non-text attachment was scrubbed" not in part:
                continue
            mime_type = self._get_part_field(part, "type")
            size = self._get_part_field(part, "size")
            url = self._get_part_field(part, "url")
            if mime_type and size and url:
                attachments.append((mime_type, size, url))
        return attachments

    def _get_part_field(self, part, name):
        fp = io.StringIO(part)
        for line in fp.readlines():
            if line.lower().startswith(name):
                return line.split(":", 1)[1].strip()
