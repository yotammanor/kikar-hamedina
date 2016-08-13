from unittest import TestCase

import django
django.setup()

import requests

from mks import Member

class MemberTestCase(TestCase):

    def test_get_homepage(self):
        response = requests.get("http://localhost:8000")
        self.assertEqual(response.status_code, 200)

    def test_get_mk_page(self):
        all_members = Member.objects.all()
        for member in enumerate(all_members):
            print member.name
