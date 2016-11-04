#!encoding utf-8
from csv import DictWriter, DictReader

from django.utils import timezone

from facebook_feeds.management.commands.kikar_base_commands import KikarCommentCommand
from facebook_feeds.models import Facebook_Status
from reporting.utils import TextProcessor

DELIMITER = '~'


class Command(KikarCommentCommand):
    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('--translate',
                            action='store_true',
                            dest='translate',
                            default=False,
                            help="translate comment data"
                            )
        parser.add_argument('--from-db',
                            action='store_true',
                            dest='from_db',
                            default=False,
                            help='use processed_content field')
        parser.add_argument('--exclude-ids-from-path',
                            action='store',
                            dest='exclude_from_path',
                            default=None,
                            help='exclude ids in file')

    def handle(self, *args, **options):
        print('Start.')

        file_name = 'content_only_{}.txt'.format(timezone.now().strftime('%Y_%m_%d_%H_%M_%S'))
        f = open(file_name, 'wb')
        field_names = [
            'content',
        ]
        csv_data = DictWriter(f, fieldnames=field_names, delimiter=DELIMITER)
        processor = TextProcessor()

        excluded_ids = []
        if options['exclude_from_path']:
            with open(options['exclude_from_path'], 'rb') as g:
                r = DictReader(g)
                excluded_ids = [x['comment_id'] for x in r]

        i = 0
        for status in Facebook_Status.objects_no_filters.filter(is_comment=False):
            for comment in status.comments.all():
                if comment.comment_id in excluded_ids:
                    continue
                if options['from_db']:
                    processed_text = comment.processed_content
                else:
                    processed_text = comment.content
                    processed_text = processor.replace_mk_names(text=processed_text,
                                                                context_status=comment.parent)
                if options['translate']:
                    processed_text = processor.request_translated_text_from_google(text=processed_text)
                processed_text = processor.replace_emojis_to_named_text(text=processed_text)
                print('writing comment {}'.format(i + 1))
                i += 1
                dict_row = {
                    'content': processor.flatten_text(processed_text, delimiter=DELIMITER),
                }
                csv_data.writerow(dict_row)

        f.close()
        print('Done.')
