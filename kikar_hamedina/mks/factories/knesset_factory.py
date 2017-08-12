import factory
from mks import models


class KnessetFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Knesset

    number = factory.Sequence(lambda n: n)
