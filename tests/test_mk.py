from unittest import TestCase

from mks.models import Member

class MemberTestCase(TestCase):

    def test_create_and_delete_memeber(self):
        new_member = Member()
        new_member.save()

        new_member.delete()