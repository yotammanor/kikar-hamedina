#!encoding utf-8
from csv import DictWriter
from facebook_feeds.management.commands.kikar_base_commands import KikarCommentCommand
from mks.models import Member
from reporting.utils import xlsx_to_dict_generator, normalize, EMOJI_DICT_UNICODE_TO_NAME
import re
from django.utils import timezone
import datetime

TAB_NAME = 'Permutations'


class Command(KikarCommentCommand):
    def text_manipulation_emojis(self, text):
        for emoji_code, emoji_name in EMOJI_DICT_UNICODE_TO_NAME.iteritems():
            text = re.sub(emoji_code, emoji_name, text, flags=re.U)
        return text

    def text_manipulation_mk_names(self, text, context_status, permutations_dict):

        base_pattern = ur"""

                            (?P<pre>                                                 # part before mk name

                                (^|[\s\t\n\r]+)                                      # either beginning or space
                                [\d\]\[\$\*\.\^\?\+=-@#%!,;:\<\>/\'\[\]\(\){{}}\\]*  # allow for special chars
                                [\u05e9\u05d1\u05dc\u05de\u05d5\u05d4]?              # leading letters in Hebrew
                            )
                           (?P<mk>{})                                                # mk name permutation formatted in

                           (?P<post>                                                 # part after mk name

                                (
                                $|                                                   # either end of text
                                [\s\t\n\r]+|                                         # or one or more space characters
                                [\d\]\[\$\*\.\^\?\+=-@#%!,;:\<\>/\'\[\]\(\){{}}\\]+  # or one or more special characters
                                )
                           )"""
        base_replace_pattern = '\g<pre>{}\g<post>'

        # get permutations for context_status.mk.id
        relevant_ids = [context_status.feed.persona.object_id]
        current_perms = []
        # build full list of permuations as regex patterns - base_name, non_writer, writer, roles
        for mk_id in relevant_ids:
            current_perms.append(permutations_dict[mk_id]['base_name'])
            current_perms += permutations_dict[mk_id]['names_as_non_writer']
            current_perms += permutations_dict[mk_id]['names_as_writer']
            if context_status.published <= timezone.datetime(2015, 3, 18, tzinfo=timezone.get_default_timezone()):
                current_perms += permutations_dict[mk_id]['roles_19th_knesset']
            else:
                current_perms += permutations_dict[mk_id]['roles_20th_knesset']
        ## handle .?!~@#$%^&*()_+~`"1234567890;,<>/[]{}\|*-+ etc. or trailing-non-letters until space
        current_perms = sorted(current_perms, key=lambda x: (len(x.split(' ')), len(x)), reverse=True)
        patterns = [base_pattern.format(perm.replace(' ', '\s')) for perm in current_perms]
        # each permutation found, replace with MK_WRITER_NAME

        for pattern in patterns:
            # text = re.sub(pattern, u'\g<pre>MK_WRITER_OF_POST\g<post>', text, re.UNICODE)
            text = re.sub(pattern, base_replace_pattern.format('MK_WRITER_OF_POST'), text, flags=re.U | re.X | re.I)

        # get permutations for all but context_status.mk.id
        relevant_ids = [x for x in permutations_dict.keys() if not x == context_status.feed.persona.object_id]
        #  build list of permutations - base_name, non_writer, roles
        current_perms = []
        for mk_id in relevant_ids:
            current_perms.append(permutations_dict[mk_id]['base_name'])
            current_perms += permutations_dict[mk_id]['names_as_non_writer']
            if context_status.published <= timezone.datetime(2015, 3, 18, tzinfo=timezone.get_default_timezone()):
                current_perms += permutations_dict[mk_id]['roles_19th_knesset']
            else:
                current_perms += permutations_dict[mk_id]['roles_20th_knesset']
        current_perms = sorted(current_perms, key=lambda x: (len(x.split(' ')), len(x)), reverse=True)
        # each permutation found, replace with MK_NON_WRITER_NAME
        patterns = [base_pattern.format(unicode(perm).replace(' ', '\s')) for perm in current_perms]
        # each permutation found, replace with MK_WRITER_NAME
        for pattern in patterns:
            # text = re.sub(pattern, base_replace_pattern.format('MK_NOT_WRITER_OF_POST'), text, re.UNICODE)
            text = re.sub(pattern, base_replace_pattern.format('MK_NOT_WRITER_OF_POST'), text, flags=re.U | re.X | re.I)

        return text


    def handle(self, *args, **options):
        print('Start.')

        comments = self.parse_comments(options)
        with open('Alternative Names.xlsx', 'rb') as f:
            permutations_dict = {}
            for row in xlsx_to_dict_generator(f, '%s' % TAB_NAME):
                row['names_as_writer'] = [x for x in normalize(row['names_as_writer']).split(';') if x]
                row['names_as_non_writer'] = [x for x in normalize(row['names_as_non_writer']).split(';') if x]
                row['roles_19th_knesset'] = [x for x in normalize(row['roles_19th_knesset']).split(';') if x]
                row['roles_20th_knesset'] = [x for x in normalize(row['roles_20th_knesset']).split(';') if x]
                permutations_dict[row['id']] = row

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

        for i, comment in enumerate(comments):
            processed_text = self.text_manipulation_mk_names(comment.content, context_status=comment.parent,
                                                             permutations_dict=permutations_dict)
            processed_text = self.text_manipulation_emojis(text=processed_text)
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
