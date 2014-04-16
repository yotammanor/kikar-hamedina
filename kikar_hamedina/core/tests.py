from django.test import TestCase
from persons.models import Party, Person
from django.db.models import Count


class TestOperationalDBStatus(TestCase):
    '''
    This Test is not Operational!
    (Read this sentence with your dark lord voice)
    '''
    def test_number_of_parties_in_db(self):
        number_of_parties = Party.objects.all().count()
        self.assertEqual(number_of_parties > 0, True)

    def test_number_of_parties_without_persons(self):
        number_of_parties_without_persons = Party.objects.annotate(num_of_persons=Count('persons')).\
            filter(num_of_persons=0).count()
        self.assertEqual(number_of_parties_without_persons==0, True)