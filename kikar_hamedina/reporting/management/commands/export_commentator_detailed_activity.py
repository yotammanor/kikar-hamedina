#!encoding utf-8
from csv import DictWriter
from collections import OrderedDict, defaultdict

from django.utils import timezone

from facebook_feeds.management.commands.kikar_base_commands import KikarBaseCommand
from facebook_feeds.models import Facebook_Feed, Facebook_Status, Facebook_User

DEFAULT_PUBLISH_YEAR = [2014, 2015]

DELIMITER = '~'


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

    def row_default_dict(self):
        return defaultdict(int)

    def build_commentator_data(self, options):
        counter = defaultdict(self.row_default_dict)

        statuses = Facebook_Status.objects.all()
        for i, status in enumerate(statuses):
            print('working on {} of {}.'.format(i + 1, len(statuses)))
            if status.is_comment:
                continue
            counter['num_of_statuses'][status.feed] += 1
            if options['type'] == 'likes':
                for like in status.likes.all():
                    counter[like.user.facebook_id][status.feed.id] += 1

            elif options['type'] == 'comments':
                for comment in status.comments.all():
                    counter[comment.comment_from.facebook_id][comment.parent.feed.id] += 1
            else:
                raise Exception('select --type "like" or "comment"')

        return counter

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
                    headers = ['commentator_id', 'commentator_type'] + [x for x in
                                                                        Facebook_Feed.objects.all().values_list('id',
                                                                                                                flat=True)]

                    print(headers)
                    csv_data = DictWriter(f, fieldnames=headers, delimiter=DELIMITER)
                    csv_data.writeheader()
                    feed_to_mk_id = {x: Facebook_Feed.objects.get(id=x).persona.content_object for x in row.keys() if
                                     x not in ['commentator_id', 'commentator_type']}
                    feed_to_mk_id['commentator_id'] = None
                    feed_to_mk_id['commentator_type'] = None
                    csv_data.writerow(feed_to_mk_id)
                    first = False
                csv_data.writerow(row)
        print('Done.')
