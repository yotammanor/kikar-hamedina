from django.core.management.base import BaseCommand
from autotag import autotag
from facebook_feeds.models import Facebook_Status
import math


class Command(BaseCommand):
    help = "My shiny new management command."

    def handle(self, *args, **options):
        print 'start.'
        all_statuses = Facebook_Status.objects.filter(tagged_items__isnull=False).order_by('?')
        print all_statuses.count()
        train_statuses = all_statuses[0:int(math.floor(all_statuses.count() / 2.0))]
        test_statuses = all_statuses[int(math.floor(all_statuses.count() / 2.0)):]
        print 'length of data: train: %d, test: %d' % (train_statuses.count(), test_statuses.count())
        train_data = []
        for status in train_statuses:
            status_dict = {'id': status.id, 'text': status.content,
                           'tags': [str(tag.tag.id) for tag in status.tagged_items.all()]}
            train_data.append(status_dict)
        test_data = []
        for status in test_statuses:
            status_dict = {'id': status.id, 'text': status.content,
                           'tags': [str(tag.tag.id) for tag in status.tagged_items.all()]}
            test_data.append(status_dict)
        at = autotag.AutoTag()
        print 'start training.'
        at.classify(train_data)
        print 'finished classifying! Start testing'

        a = at.test(test_data)
        print a
        print 'done.'

