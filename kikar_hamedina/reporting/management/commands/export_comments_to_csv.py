#!encoding utf-8
from csv import DictWriter
from facebook_feeds.management.commands.kikar_base_commands import KikarCommentCommand
from reporting.utils import TextProcessor

DELIMITER = '~'


class Command(KikarCommentCommand):
    def handle(self, *args, **options):
        print('Start.')

        comments = self.parse_comments(options)
        f = open('{}_full_data.csv'.format(options['file_path'].split('.csv')[0]), 'wb')
        field_names = [
            'comment_id',
            'mk_id',
            'mk_name',
            'parent_status_id',
            'parent_status_content',
            'parent_status_link',
            'comment_link',
            'content',
            'content_processed',
            'published',
            'commentator_id',
            'like_count',
            'comment_count',
        ]
        csv_data = DictWriter(f, fieldnames=field_names, delimiter=DELIMITER)
        headers = {field_name: field_name for field_name in field_names}
        csv_data.writerow(headers)

        processor = TextProcessor()

        for i, comment in enumerate(comments):
            processed_text = processor.text_manipulation_mk_names(text=comment.content, context_status=comment.parent)
            processed_text = processor.text_manipulation_emojis(text=processed_text)
            print('writing comment {} of {}'.format(i + 1, comments.count()))
            dict_row = {
                'comment_id': comment.comment_id,
                'mk_id': comment.status.feed.persona.content_object.id,
                'mk_name': comment.status.feed.persona.content_object.name,
                'parent_status_id': comment.parent.status_id,
                'parent_status_content': processor.text_manipulation_flatten_text(comment.parent.content,
                                                                                  delimiter=DELIMITER),
                'parent_status_link': comment.parent.get_link,
                'comment_link': 'www.facebook.com/{}'.format(comment.comment_id),
                'content': processor.text_manipulation_flatten_text(comment.content, delimiter=DELIMITER),
                'content_processed': processor.text_manipulation_flatten_text(processed_text, delimiter=DELIMITER),
                'published': comment.published,
                'commentator_id': comment.comment_from.facebook_id,
                'like_count': comment.like_count,
                'comment_count': comment.comment_count
            }
            csv_data.writerow(dict_row)

        f.close()
        print('Done.')
