from unittest import TestCase

import django
django.setup()

import requests

import mks


class MemberTestCase(TestCase):

    def test_create_and_delete_memeber(self):
        new_member = mks.Member()
        new_member.save()

        new_member.delete()

    def test_localrequest(self):
        response = requests.get("http://localhost:8000")
        self.assertEqual(response.status_code, 200)