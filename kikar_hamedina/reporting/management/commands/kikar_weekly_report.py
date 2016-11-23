# encoding: utf-8

import StringIO
from optparse import make_option, OptionParser
from time import sleep
import numpy as np

import pandas as pd
from pandas import ExcelWriter

from django.utils import timezone
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.core.management.base import BaseCommand

from core.insights import StatsEngine, Stats, get_times
from core.models import MEMBER_MODEL, PARTY_MODEL

from facebook_feeds.models import Facebook_Feed, Facebook_Status

from reporting.models import WeeklyReportRecipients


def split_by_comma(option, opt, value, parser):
    setattr(parser.values, option.dest, [x.strip() for x in value.split(',')])


IS_ELECTIONS_MODE = getattr(settings, 'IS_ELECTIONS_MODE', False)


class Command(BaseCommand):
    help = "Calculate site stats and email it."

    recipients = make_option('-m',
                             '--mail-recipients',
                             type='string',
                             action='callback',
                             dest='recipients',
                             callback=split_by_comma,
                             help='set emails, seperated by value')

    recipients_from_db = make_option('-d',
                                     '--recipients-from-db',
                                     action='store_true',
                                     dest='recipients_from_db',
                                     help='add this flag to send report based on emails from db.')

    beta_recipients_from_db = make_option('-b',
                                          '--beta-recipients-from-db',
                                          action='store_true',
                                          dest='beta_recipients_from_db',
                                          help='add this flag to send report based on emails from db marked as beta only.')

    option_list_helper = list()
    for x in BaseCommand.option_list:
        option_list_helper.append(x)
    option_list_helper.append(recipients)
    option_list_helper.append(recipients_from_db)
    option_list_helper.append(beta_recipients_from_db)
    option_list = tuple(option_list_helper)

    def feed_and_group_stats(self):
        stats = Stats()
        engine = stats.engine

        feeds = Facebook_Feed.current_feeds.all()

        feeds_data = []
        for feed in feeds:

            week_status_set = feed.facebook_status_set_no_filters.filter(
                published__gte=timezone.now() - timezone.timedelta(days=7))

            num_of_weekly_statuses = engine.n_statuses_last_week([feed.id])
            total_like_count_weekly = engine.total_status_likes_last_week([feed.id])
            mean_like_count_weekly = engine.mean_status_likes_last_week([feed.id])
            mean_comment_count_weekly = engine.mean_status_comments_last_week([feed.id])
            mean_share_count_weekly = engine.mean_status_shares_last_week([feed.id])
            feeds_data.append({'feed_id': feed.id,
                               'feed_name': feed.persona.owner.name,
                               'feed_type': feed.feed_type,
                               'num_of_weekly_statuses': num_of_weekly_statuses,
                               'total_like_count_this_week': total_like_count_weekly,
                               'mean_like_count_this_week': mean_like_count_weekly,
                               'mean_comment_count_this_week': mean_comment_count_weekly,
                               'mean_share_count_this_week': mean_share_count_weekly,
                               'top_status_by_like_count_this_week': getattr(week_status_set.order_by(
                                   '-like_count').first(), 'like_count', 0),
                               'top_status_by_share_count_this_week': getattr(week_status_set.order_by(
                                   '-share_count').first(), 'share_count', 0),
                               'top_status_by_comment_count_this_week': getattr(week_status_set.order_by(
                                   '-comment_count').first(), 'comment_count', 0),
                               'current_followers_count': feed.current_fan_count,
                               'current_talking_about_count': getattr(feed.feed_popularity_set.order_by(
                                   '-date_of_creation').first(), 'talking_about_count', -1),
                               'change_in_followers_count_since_last_week': feed.popularity_dif(days_back=7,
                                                                                                return_value='fan_count_dif_nominal')

            })

        parties_data = list()
        party_ids = dict()
        for party in stats.party_list:
            all_members_for_party = PARTY_MODEL.objects.get(id=party.party.id).current_members()
            all_feeds_for_party = [member.facebook_persona.get_main_feed.id for member in
                                   all_members_for_party if member.facebook_persona]
            party_ids[party.party.id] = all_feeds_for_party
            parties_data.append({
                'party_id': party.party.id,
                'party_name': party.party.name,
                'num_of_weekly_statuses': getattr(party, 'n_statuses_last_week', 0),
                'total_like_count_this_week': getattr(party, 'total_status_likes_last_week', 0),
                'mean_like_count_this_week': getattr(party, 'mean_status_likes_last_week', 0),
                'mean_comment_count_this_week': getattr(party, ' mean_status_comments_last_week', 0),
                'mean_share_count_this_week': getattr(party, 'mean_status_shares_last_week', 0)
            })

        PARTY_NAME_FORMAT = '; '
        print 'is election mode:', IS_ELECTIONS_MODE
        if not IS_ELECTIONS_MODE:
            factions = [{'id': 1,
                         'name': 'right_side',
                         'members': PARTY_NAME_FORMAT.join(
                             [x.name for x in PARTY_MODEL.objects.filter(id__in=[27, 30, 31])]),
                         'feeds': party_ids[27] + party_ids[30] + party_ids[31],
                         'size': PARTY_MODEL.objects.get(id=27).number_of_members +
                                 PARTY_MODEL.objects.get(id=30).number_of_members +
                                 PARTY_MODEL.objects.get(id=31).number_of_members
                        },
                        {'id': 2,
                         'name': 'center_side',
                         'members': PARTY_NAME_FORMAT.join(
                             [x.name for x in PARTY_MODEL.objects.filter(id__in=[29, 32])]),
                         'feeds': party_ids[29] + party_ids[32],
                         'size': PARTY_MODEL.objects.get(id=29).number_of_members +
                                 PARTY_MODEL.objects.get(id=32).number_of_members
                        },
                        {'id': 3,
                         'name': 'left_side',
                         'members': PARTY_NAME_FORMAT.join(
                             [x.name for x in PARTY_MODEL.objects.filter(id__in=[28, 33])]),
                         'feeds': party_ids[28] + party_ids[33],
                         'size': PARTY_MODEL.objects.get(id=28).number_of_members +
                                 PARTY_MODEL.objects.get(id=33).number_of_members
                        },
                        {'id': 4,
                         'name': 'arab_parties',
                         'members': PARTY_NAME_FORMAT.join(
                             [x.name for x in PARTY_MODEL.objects.filter(id__in=[35])]),
                         'feeds': party_ids[35],
                         'size': PARTY_MODEL.objects.get(id=35).number_of_members
                        },
                        {'id': 5,
                         'name': 'haredi_parties',
                         'members': PARTY_NAME_FORMAT.join(
                             [x.name for x in PARTY_MODEL.objects.filter(id__in=[36, 34])]),
                         'feeds': party_ids[36] + party_ids[34],
                         'size': PARTY_MODEL.objects.get(id=36).number_of_members +
                                 PARTY_MODEL.objects.get(id=34).number_of_members
                        },
            ]
        else:  # IS_ELECTION_MODE
            factions = [{'id': 1,
                         'name': 'right_side',
                         'members': PARTY_NAME_FORMAT.join(
                             [x.name for x in PARTY_MODEL.objects.filter(id__in=[26, 28, 29])]),
                         'feeds': party_ids[26] + party_ids[28] + party_ids[29],
                         'size': PARTY_MODEL.objects.get(id=26).candidates.count() +
                                 PARTY_MODEL.objects.get(id=28).candidates.count() +
                                 PARTY_MODEL.objects.get(id=29).candidates.count()
                        },
                        {'id': 2,
                         'name': 'center_side',
                         'members': PARTY_NAME_FORMAT.join(
                             [x.name for x in PARTY_MODEL.objects.filter(id__in=[30, 31])]),
                         'feeds': party_ids[30] + party_ids[31],
                         'size': PARTY_MODEL.objects.get(id=30).candidates.count() +
                                 PARTY_MODEL.objects.get(id=31).candidates.count()
                        },
                        {'id': 3,
                         'name': 'left_side',
                         'members': PARTY_NAME_FORMAT.join(
                             [x.name for x in PARTY_MODEL.objects.filter(id__in=[27, 32])]),
                         'feeds': party_ids[27] + party_ids[32],
                         'size': PARTY_MODEL.objects.get(id=27).candidates.count() +
                                 PARTY_MODEL.objects.get(id=32).candidates.count()
                        },
                        {'id': 4,
                         'name': 'arab_parties',
                         'members': PARTY_NAME_FORMAT.join(
                             [x.name for x in PARTY_MODEL.objects.filter(id__in=[36])]),
                         'feeds': party_ids[36],
                         'size': PARTY_MODEL.objects.get(id=36).candidates.count()
                        },
                        {'id': 5,
                         'name': 'haredi_parties',
                         'members': PARTY_NAME_FORMAT.join(
                             [x.name for x in PARTY_MODEL.objects.filter(id__in=[33, 34, 35])]),
                         'feeds': party_ids[33] + party_ids[34] + party_ids[35],
                         'size': PARTY_MODEL.objects.get(id=33).candidates.count() +
                                 PARTY_MODEL.objects.get(id=34).candidates.count() +
                                 PARTY_MODEL.objects.get(id=35).candidates.count()
                        },
            ]
        factions_data = list()
        for fact in factions:
            factions_data.append({
                'faction_id': fact['id'],
                'faction_name': fact['name'],
                'faction_members': fact['members'],
                'num_of_members_in_faction': fact['size'],
                'num_of_feeds_in_faction': len(fact['feeds']),
                'num_of_weekly_statuses': engine.n_statuses_last_week(fact['feeds']),
                'total_like_count_this_week': engine.total_status_likes_last_week(fact['feeds']),
                'mean_like_count_this_week': engine.mean_status_likes_last_week(fact['feeds']),
                'mean_comment_count_this_week': engine.mean_status_comments_last_week(fact['feeds']),
                'mean_share_count_this_week': engine.mean_status_shares_last_week(fact['feeds']),
            })

        meta_data = []

        return feeds_data, parties_data, factions_data, meta_data

    def statuses_data(self):
        week_ago, month_ago = get_times()
        start_date = timezone.datetime(2014, 10, 25, 0, 0, 0, 0, tzinfo=timezone.get_current_timezone())
        week_statuses = Facebook_Status.objects.filter(published__gte=start_date, like_count__isnull=False)
        week_statuses_build = [(status.status_id, status.feed.id, status.feed.name,
                                status.feed.persona.owner.current_party.id,
                                status.feed.persona.owner.current_party.name,
                                status.published, status.is_deleted,
                                status.like_count, status.share_count, status.comment_count,
                                ';'.join([tagged_item.tag.name for tagged_item in
                                          status.tagged_items.filter(tagged_by__username='karineb')]),
                                ';'.join([tagged_item.tag.name for tagged_item in
                                          status.tagged_items.all()]),
                                status.get_link,
                                u'שחיתות' in status.content,
                                u'בטחון' in status.content or u'ביטחון' in status.content,
                                u'חברה' in status.content or u'חברתי' in status.content,
                                u'טרור' in status.content,
                                u'כלכל' in status.content,
                                u'שקיפות' in status.content,
                                u'שוויון' in status.content,
                                u'זכויות' in status.content,
                                u'שלום' in status.content,
                                u'פלסטינים' in status.content,
                                u'יהודי' in status.content or u'יהדות' in status.content,
                                u'ריבונ' in status.content,
                                u'סיפוח' in status.content,
                                u'מסורת' in status.content,
                                u'דת' in status.content,
                                u'כבוד' in status.content,
                                u'מלחמ' in status.content,
                                u'ציונ' in status.content,
                                u'חינוך' in status.content,
                                u'בריאות' in status.content,
                                u'תעסוק' in status.content,
                                u'רווחה' in status.content,
                                u'מזרחי' in status.content
                               ) for
                               status in week_statuses]
        field_names = ['status_id', 'feed_id', 'feed_name', 'party_id', 'party_name',
                       'published', 'is_deleted',
                       'like_count', 'share_count', 'comment_count',
                       'tags_by_karine', 'tags', 'link',
                       u'has_word_שחיתות',
                       u'has_word_בטחון_or_ביטחון',
                       u'has_word_חברה_or_חברתי',
                       u'has_word_טרור',
                       u'has_word_כלכל',
                       u'has_word_שקיפות',
                       u'has_word_שוויון',
                       u'has_word_זכויות',
                       u'has_word_שלום',
                       u'has_word_פלסטינים',
                       u'has_word_יהודי_or_יהדות',
                       u'has_word_ריבונ',
                       u'has_word_סיפוח',
                       u'has_word_מסורת',
                       u'has_word_דת',
                       u'has_word_כבוד',
                       u'has_word_מלחמ',
                       u'has_word_ציונ',
                       u'has_word_חינוך',
                       u'has_word_בריאות',
                       u'has_word_תעסוק',
                       u'has_word_רווחה',
                       u'has_word_מזרחי'

        ]
        recs = np.core.records.fromrecords(week_statuses_build, names=field_names)
        week_statuses = pd.DataFrame.from_records(recs, coerce_float=True)
        return week_statuses

    def build_and_send_email(self, data, options):
        date = timezone.now().date().strftime('%Y_%m_%d')

        if options['beta_recipients_from_db']:
            print 'beta recipients requested from db.'
            recipients = [a.email for a in WeeklyReportRecipients.objects.filter(is_active=True, is_beta=True)]
        elif options['recipients_from_db']:
            print 'recipients requested from db.'
            recipients = [a.email for a in WeeklyReportRecipients.objects.filter(is_active=True)]

        elif options['recipients']:
            print 'manual recipients requested.'
            recipients = options['recipients']
        else:
            print 'no recipients requested.'
            recipients = settings.DEFAULT_WEEKLY_RECIPIENTS

        if not recipients:
            print 'no recipients in db.'
            recipients = settings.DEFAULT_WEEKLY_RECIPIENTS

        print 'recipients:', recipients

        message = EmailMessage(subject='Kikar Hamedina, Weekly Report: %s' % date,
                               body='Kikar Hamedina, Weekly Report: %s.' % date,
                               to=recipients)
        w = ExcelWriter('Weekly_report_%s.xlsx' % date)

        for datum in data:
            # csvfile = StringIO.StringIO()
            pd.DataFrame.from_dict(datum['content']).to_excel(w, sheet_name=datum['name'])

        w.save()
        w.close()
        # f = open(w.path, 'r', encoding='utf-8')
        message.attach_file(w.path)
        message.send()

    def handle(self, *args, **options):

        feeds_data, parties_data, factions_data, meta_data = self.feed_and_group_stats()
        week_statuses = self.statuses_data()

        all_data = [{'name': 'feeds_data',
                     'content': feeds_data},
                    {'name': 'parties_data',
                     'content': parties_data},
                    {'name': 'factions_data',
                     'content': factions_data},
                    {'name': 'week_statuses',
                     'content': week_statuses},
        ]

        print 'Sending email..'
        self.build_and_send_email(all_data, options)
        print 'Done.'