#!encoding utf-8
from csv import DictWriter
from facebook_feeds.management.commands.kikar_base_commands import KikarCommentCommand
from reporting.utils import xlsx_to_dict_generator, normalize, TextProcessor





class Command(KikarCommentCommand):
    def handle(self, *args, **options):
        print('Start.')

        comments = self.parse_comments(options)
        f = open('{}_full_data.csv'.format(options['file_path'].split('.csv')[0]), 'wb')
        field_names = [
            'comment_id',
            'parent_status_id',
            'link',
            'content',
            'published',
            'commentator_id',
            'like_count',
            'comment_count',
            'content_processed'
        ]
        csv_data = DictWriter(f, fieldnames=field_names, delimiter='~')
        headers = {field_name: field_name for field_name in field_names}
        csv_data.writerow(headers)

        processor = TextProcessor()

        for i, comment in enumerate(comments):
            processed_text = processor.text_manipulation_mk_names(text=comment.content, context_status=comment.parent)
            processed_text = processor.text_manipulation_emojis(text=processed_text)
            print('writing comment {} of {}'.format(i + 1, comments.count()))
            dict_row = {
                'comment_id': comment.comment_id,
                'parent_status_id': comment.parent.status_id,
                'link': 'www.facebook.com/{}'.format(comment.comment_id),
                'content': unicode(comment.content).encode('utf-8').replace('\r\n', '\t\t').replace('~', '*').replace(
                    '\n',
                    '\t'),
                'published': comment.published,
                'commentator_id': comment.comment_from.facebook_id,
                'like_count': comment.like_count,
                'comment_count': comment.comment_count,
                'content_processed': unicode(processed_text).encode('utf-8').replace('\r\n', '\t\t').replace('~',
                                                                                                             '*').replace(
                    '\n',
                    '\t')
            }
            csv_data.writerow(dict_row)

        f.close()
        print('Done.')
