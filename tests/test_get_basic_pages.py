from django.test import TestCase
from django.test import Client as TestingClient

import django
django.setup()

class BasicPagesTestCase(TestCase):

    def setUp(self):
        self.client = TestingClient()

        # Hardcoded configurations
        self.member_id = "731"
        self.party_id = "32"

    def test_get_homepage(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_get_mk_page(self):
        mk_page_url = "/member/{member_id}".format(member_id=self.member_id)
        response = self.client.get(mk_page_url)
        self.assertEqual(response.status_code, 200)

    # def test_get_party_page(self):
    #     party_page_url = "/party/{party_id}".format(party_id=self.party_id)
    #     response = self.client.get(party_page_url)
    #     self.assertEqual(response.status_code, 200)
    #
    # def test_get_search_page(self):
    #     response = self.client.get("/search/")
    #     self.assertEqual(response.status_code, 200)
    #
    # def test_get_about_page(self):
    #     response = self.client.get("/about/")
    #     self.assertEqual(response.status_code, 200)

