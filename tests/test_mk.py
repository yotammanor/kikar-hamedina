from unittest import TestCase

import django
django.setup()

import requests
from logging import getLogger

logger = getLogger("my_logger")

from mks import Member

class MemberTestCase(TestCase):

    def test_get_homepage(self):
        response = requests.get("http://localhost:8000")
        self.assertEqual(response.status_code, 200)

    def test_get_mk_page(self):
        response = requests.get("http://localhost:8000/member/19")
        self.assertEqual(response.status_code, 200)


