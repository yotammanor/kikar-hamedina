from unittest import TestCase

import django
django.setup()

import mks

class MemberTestCase(TestCase):

    def test_create_and_delete_memeber(self):
        new_member = mks.Member()
        new_member.save()

        new_member.delete()