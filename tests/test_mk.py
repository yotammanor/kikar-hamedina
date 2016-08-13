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
        new_member = Member()
        new_member.name = "MOCK NAME"
        new_member.save()

        response = requests.get("http://localhost:8000/member/"+str(new_member.id))
        self.assertTrue(new_member.name in response.content)
        self.assertEqual(response.status_code, 200)

        new_member.delete()


