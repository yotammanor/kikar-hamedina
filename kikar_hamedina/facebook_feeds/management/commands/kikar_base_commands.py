import dateutil
import logging
import facebook

from csv import DictReader

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from facebook_feeds.models import Facebook_Status, Facebook_Status_Comment

FACEBOOK_API_VERSION = getattr(settings, 'FACEBOOK_API_VERSION', 'v2.5')
NUMBER_OF_TRIES_FOR_REQUEST = getattr(settings, 'NUMBER_OF_TRIES_FOR_REQUEST', 2)


class KikarBaseCommand(BaseCommand):
    graph = facebook.GraphAPI()
    api_version = FACEBOOK_API_VERSION
    tries_per_request = NUMBER_OF_TRIES_FOR_REQUEST

    def handle(self, *args, **options):
        pass


class KikarCommentCommand(KikarBaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--file',
                            action='store',
                            dest='file_path',
                            default=None,
                            help="execute on list of comment ids from file"
                            )

    def parse_comments(self, options):
        list_of_comments = list()
        if options['file_path']:
            with open(options['file_path'], 'r') as f:
                reader = DictReader(f)
                list_of_comment_ids = [x['comment_id'] for x in reader]
                list_of_comments = Facebook_Status_Comment.objects.filter(comment_id__in=list_of_comment_ids)
        return list_of_comments


class KikarStatusCommand(KikarBaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('status_id', nargs='?', type=str)
        parser.add_argument('-f',
                            '--force-update',
                            action='store_true',
                            dest='force-update',
                            default=False,
                            help='Force update of status.'),
        parser.add_argument('-a',
                            '--force-attachment-update',
                            action='store_true',
                            dest='force-attachment-update',
                            default=False,
                            help='Use this flag to force updating of status attachment'),
        parser.add_argument('--from-date',
                            action='store',
                            type=str,
                            dest='from-date',
                            default=None,
                            help="Specify date from which to update the statuses (inclusive) e.g. 2014-03-31"),
        parser.add_argument('--to-date',
                            action='store',
                            type=str,
                            dest='to-date',
                            default=None,
                            help='Specify date until which to update the statuses (exclusive) e.g. 2014-03-31'),
        parser.add_argument('--feed-ids',
                            action='store',
                            type=str,
                            dest='feed-ids',
                            default=None,
                            help='Specify particular feed ids you want to update likes for with list of ids (e.g. 51, 54)'),
        parser.add_argument('--update-deleted',
                            action='store_true',
                            dest='update-deleted',
                            default=False,
                            help="Update is_deleted flag: set to True/False for deleted/existing statuses"),
        parser.add_argument('--file',
                            action='store',
                            dest='file_path',
                            default=None,
                            help="execute on list of status ids from file"),
        parser.add_argument('--skip',
                            action='store_true',
                            dest='skip',
                            default=False,
                            help="skip statuses that has data for them"),

    def parse_statuses(self, args, options):
        list_of_statuses = list()
        # Case no args - fetch all statuses or by options
        if len(args) == 0:
            criteria = {}
            if options['from-date']:
                criteria['published__gte'] = dateutil.parser.parse(options['from-date'])
            if options['to-date']:
                criteria['published__lt'] = dateutil.parser.parse(options['to-date'])
            if options['feed-ids']:
                criteria['feed__id__in'] = options['feed-ids'].split(',')
            db_statuses = Facebook_Status.objects_no_filters.filter(**criteria).order_by('-published')
            list_of_statuses = list(db_statuses)

            if options['file_path']:
                with open(options['file_path'], 'r') as f:
                    reader = DictReader(f)
                    list_of_status_ids = [x['status_id'] for x in reader]
                    list_of_statuses = Facebook_Status.objects.filter(status_id__in=list_of_status_ids)

        # Case arg exists - fetch status by id supplied
        elif len(args) == 1:
            status_id = args[0]
            try:
                status = Facebook_Status.objects_no_filters.get(status_id=status_id)
                list_of_statuses.append(status)

            except Facebook_Status.DoesNotExist:
                warning_msg = "Status #({0}) does not exist.".format(status_id)
                logger = logging.getLogger('django')
                logger.warning(warning_msg)
                raise CommandError('Status "%s" does not exist' % status_id)

        # Case invalid args
        else:
            raise CommandError('Please enter a valid status id')
        self.stdout.write('Working on total of {0} statuses'.format(len(list_of_statuses)))
        return list_of_statuses
