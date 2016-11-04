#!encoding utf-8
from csv import DictWriter
from collections import OrderedDict, defaultdict

from django.utils import timezone

from facebook_feeds.management.commands.kikar_base_commands import KikarBaseCommand
from facebook_feeds.models import Facebook_Feed, Facebook_Status, Facebook_User

from functools32 import lru_cache

DEFAULT_PUBLISH_YEAR = [2014, 2015]

DELIMITER = ','

from reporting.utils import TextProcessor


class Command(KikarBaseCommand):
    def add_arguments(self, parser):

        parser.add_argument('--feed',
                            action='store',
                            dest='feed',
                            default=None,
                            help="choose year to filter on"
                            )

        parser.add_argument('--type',
                            action='store',
                            dest='type',
                            help="collect comments or likes"
                            )
        parser.add_argument('--count-commentator-once',
                            action='store_true',
                            default=False,
                            dest='count_commentator_once_per_status',
                            help="method of counting commentator - once per status, or total number of"
                                 " comments"
                            )

    def row_default_dict(self):
        return defaultdict(int)

    def build_commentator_data(self, options):
        counter = defaultdict(self.row_default_dict)

        if options['type'] == 'likes':
            facebook_users = Facebook_User.objects.all()
            number_of_users = facebook_users.count()
            for index in xrange(number_of_users):
                facebook_user = facebook_users[index]
                print('working on user {}.'.format(index + 1))

                for status_like in facebook_user.likes.all():
                    if not status_like.status.is_comment:
                        counter[facebook_user.facebook_id][status_like.status.feed.id] += 1

        elif options['type'] == 'comments':
            statuses = Facebook_Status.objects.all()
            for i, status in enumerate(statuses):
                print('working on status {} of {}.'.format(i + 1, len(statuses)))
                if status.is_comment:
                    continue
                counter['num_of_statuses'][status.feed.id] += 1
                if options['count_commentator_once_per_status']:
                    commentator_ids = []
                    for comment in status.comments.all():
                        commentator_ids.append(comment.comment_from.facebook_id)
                    unique_commentator_ids = list(set(commentator_ids))
                    for commentator_id in unique_commentator_ids:
                        counter[commentator_id][comment.parent.feed.id] += 1
                else:
                    for comment in status.comments.all():
                        counter[comment.comment_from.facebook_id][comment.parent.feed.id] += 1

        else:
            raise Exception('select --type "like" or "comment"')

        return counter

    def is_status_commented_on_by_commentator(self, commentator, status):
        return commentator.comments.filter(parent__status_id=status.status_id).exists()

    def handle(self, *args, **options):
        print('Start.')

        commentator_data = self.build_commentator_data(options)
        file_name = 'commentator_detailed_data_{}_{}.csv'.format(options['type'],
                                                                 timezone.now().strftime('%Y_%m_%d_%H_%M_%S'))
        with open(file_name, 'wb') as f:
            first = True
            for i, commentator_id in enumerate(commentator_data.keys()):
                print('writing data on commentator {}'.format(i + 1))
                if commentator_id == 'num_of_statuses':
                    continue
                commentator = Facebook_User.objects.get(facebook_id=commentator_id)
                row = OrderedDict(**{'commentator_id': commentator.facebook_id,
                                     'commentator_type': commentator.type
                                     })
                for feed_id, count_of_value in commentator_data[commentator.facebook_id].iteritems():
                    row[feed_id] = count_of_value

                if first:
                    csv_data = self.create_dict_writer(f)
                    self.write_headers(csv_data)
                    self.write_feed_related_details(csv_data, row)
                    self.write_totals(commentator_data, csv_data)
                    first = False
                csv_data.writerow(row)
        print('Done.')

    def write_headers(self, csv_data):
        csv_data.writeheader()

    def write_totals(self, commentator_data, csv_data):
        feed_ids = self.get_all_feed_ids()
        totals = {x: commentator_data['num_of_statuses'][x] for x in feed_ids}
        totals = self.add_empty_commentator_rows(totals, commentator_id='number_of_posts')
        csv_data.writerow(totals)

    def add_empty_commentator_rows(self, row, commentator_id=None, commentator_type=None):
        row['commentator_id'] = commentator_id
        row['commentator_type'] = commentator_type
        return row

    def write_feed_related_details(self, csv_data, row):
        feed_ids = self.get_all_feed_ids()
        self.write_mk_id(csv_data, feed_ids)
        self.write_mk_name(csv_data, feed_ids)
        self.write_party_name(csv_data, feed_ids)

    def write_mk_id(self, csv_data, feed_ids):
        feed_to_mk_id = {x: self.get_mk_id_if_exists(x) for x in feed_ids}
        feed_to_mk_id = self.add_empty_commentator_rows(feed_to_mk_id, commentator_id='MK_ID')
        csv_data.writerow(feed_to_mk_id)

    def write_mk_name(self, csv_data, feed_ids):
        processor = TextProcessor()
        feed_to_mk_id = {x: processor.flatten_text(self.get_mk_name_if_exists(x), delimiter=DELIMITER) for x in
                         feed_ids}
        feed_to_mk_id = self.add_empty_commentator_rows(feed_to_mk_id, commentator_id='MK_ID')
        csv_data.writerow(feed_to_mk_id)

    def write_party_name(self, csv_data, feed_ids):
        processor = TextProcessor()
        feed_to_mk_id = {x: processor.flatten_text(self.get_party_name_if_exists(x), delimiter=DELIMITER) for x in
                         feed_ids}
        feed_to_mk_id = self.add_empty_commentator_rows(feed_to_mk_id, commentator_id='MK_ID')
        csv_data.writerow(feed_to_mk_id)

    def get_mk_id_if_exists(self, feed_id):
        content_object = self.get_content_object_for_feed_id(feed_id)
        if content_object:
            return content_object.id
        return None

    def get_mk_name_if_exists(self, feed_id):
        content_object = self.get_content_object_for_feed_id(feed_id)
        if content_object:
            return content_object.name
        return None

    def get_party_name_if_exists(self, feed_id):
        content_object = self.get_content_object_for_feed_id(feed_id)
        if content_object:
            return content_object.current_party.name
        return None

    @lru_cache(maxsize=180)
    def get_content_object_for_feed_id(self, feed_id):
        return Facebook_Feed.objects.get(id=feed_id).persona.content_object

    def create_dict_writer(self, f):
        headers = ['commentator_id', 'commentator_type'] + \
                  self.get_all_feed_ids()
        csv_data = DictWriter(f, fieldnames=headers, delimiter=DELIMITER)
        return csv_data

    def get_all_feed_ids(self):
        return [x for x in Facebook_Feed.objects.all().values_list('id', flat=True)]
