from django.core.management.base import BaseCommand
from autotag import autotag
from facebook_feeds.models import Facebook_Status
import math
from random import shuffle, sample

from kikartags.utils import build_classifier_format

NUM_OF_NEGATIVE_OR_POSITIVE_STATUSES = 100
MINIMAL_NUM_OF_POSITIVE_STATUSES_FOR_TRAIN = 50
MINIMAL_NUM_OF_POSITIVE_STATUSES_FOR_TEST = 10

TOTAL_TRAIN = 100
TOTAL_TEST = 100

CLASSIFICATION_DATA_PATH = 'classification_data'


class Command(BaseCommand):
    help = "Train the classifier for a given tag id."
    args = '<tag_id>'

    def create_groups_for_test_and_train(self, tag_id):

        # Prepare positive data:

        positive_statuses = Facebook_Status.objects.filter(tagged_items__tag__id=tag_id)
        print 'num of postive statuses:', positive_statuses.count()
        if positive_statuses < MINIMAL_NUM_OF_POSITIVE_STATUSES_FOR_TRAIN + MINIMAL_NUM_OF_POSITIVE_STATUSES_FOR_TEST:
            raise Exception('Not enough positive statuses.')

        positive_status_data = [build_classifier_format(x) for x in positive_statuses]
        shuffle(positive_status_data)

        if positive_status_data > MINIMAL_NUM_OF_POSITIVE_STATUSES_FOR_TRAIN * 2:
            positive_status_data = positive_status_data[:(MINIMAL_NUM_OF_POSITIVE_STATUSES_FOR_TRAIN * 2) + 1]

        train_positive_statuses = positive_status_data[:MINIMAL_NUM_OF_POSITIVE_STATUSES_FOR_TRAIN]
        test_positive_statuses = positive_status_data[MINIMAL_NUM_OF_POSITIVE_STATUSES_FOR_TRAIN:]

        print 'train_positive_statuses: %s, test_positive_statuses: %s' % (
        len(train_positive_statuses), len(test_positive_statuses))

        # prepare negative data:

        missing_train = TOTAL_TRAIN - len(train_positive_statuses)
        missing_test = TOTAL_TEST - len(test_positive_statuses)

        status_ids = [x[0] for x in Facebook_Status.objects.filter(tagged_items__isnull=False).exclude(
            tagged_items__tag__id=tag_id).values_list('status_id')]
        rand_ids = sample(status_ids, missing_train + missing_test)
        negative_statuses = Facebook_Status.objects.filter(status_id__in=rand_ids)

        negative_statuses_data = [build_classifier_format(x) for x in negative_statuses[:missing_test + missing_train]]

        train_statuses = train_positive_statuses + negative_statuses_data[:missing_train]
        test_statuses = test_positive_statuses + negative_statuses_data[missing_train:]

        print 'train_statuses: %s, test_statuses: %s' % (len(train_statuses), len(test_statuses))

        if len(train_statuses + test_statuses) < MINIMAL_NUM_OF_POSITIVE_STATUSES_FOR_TRAIN:
            raise Exception('Not enough statuses: %d' % len(train_statuses + test_statuses))

        return train_statuses, test_statuses

    def handle(self, *args, **options):
        print 'start.'
        # all_statuses = Facebook_Status.objects.filter(tagged_items__isnull=False).order_by('?')
        # train_statuses = all_statuses[0:int(math.floor(all_statuses.count() / 2.0))]
        # test_statuses = all_statuses[int(math.floor(all_statuses.count() / 2.0)):]
        # print all_statuses.count()
        if len(args) == 0:
            raise Exception('Missing Tag ID')
        elif len(args) > 1:
            raise Exception('Too many Tag IDs')

        tag_id = args[0]
        print 'tag_id:', tag_id

        train_statuses, test_statuses = self.create_groups_for_test_and_train(tag_id)
        at = autotag.AutoTag(CLASSIFICATION_DATA_PATH)
        print 'start training.'
        at.classify(train_statuses, MINIMAL_NUM_OF_POSITIVE_STATUSES_FOR_TRAIN)
        print 'finished classifying! Start testing'

        a = at.test(test_statuses)
        print a
        print 'done.'

