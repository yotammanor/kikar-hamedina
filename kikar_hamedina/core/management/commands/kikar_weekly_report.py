import StringIO

from mks.models import Party
from facebook_feeds.models import Facebook_Feed, Facebook_Status
from core.insights import StatsEngine, Stats, get_times
import pandas as pd
import numpy as np

from django.utils import timezone
from django.core.mail import send_mail, EmailMessage
from django.conf import settings

from django.core.management.base import BaseCommand


def feed_and_group_stats():
    stats = Stats()
    engine = stats.engine

    feeds = Facebook_Feed.current_feeds.all()

    feeds_data = []
    for feed in feeds:
        num_of_weekly_statuses = engine.n_statuses_last_week([feed.id])
        mean_like_count_weekly = engine.mean_status_likes_last_week([feed.id])
        mean_comment_count_weekly = engine.mean_status_comments_last_week([feed.id])
        mean_share_count_weekly = engine.mean_status_shares_last_week([feed.id])
        feeds_data.append({'feed_id': feed.id,
                           'feed_name': feed.name or feed.persona.content_object.name,
                           'num_of_weekly_statuses': num_of_weekly_statuses,
                           'mean_like_count_this_week': mean_like_count_weekly,
                           'mean_comment_count_this_week': mean_comment_count_weekly,
                           'mean_share_count_this_week': mean_share_count_weekly,
                           'popularity_count': feed.current_fan_count,
                           'change_since_last_week': feed.popularity_dif(days_back=7,
                                                                         return_value='fan_count_dif_nominal')

        })

    parties_data = list()
    party_ids = dict()
    for party in stats.party_list:
        all_members_for_party = Party.objects.get(id=party.party.id).current_members()
        all_feeds_for_party = [member.facebook_persona.get_main_feed.id for member in
                               all_members_for_party if member.facebook_persona]
        party_ids[party.party.id] = all_feeds_for_party
        parties_data.append({
            'party_id': party.party.id,
            'party_name': party.party.name,
            'num_of_weekly_statuses': party.n_statuses_last_week,
            'mean_like_count_this_week': party.mean_status_likes_last_week,
            'mean_comment_count_this_week': party.mean_status_comments_last_week,
            'mean_share_count_this_week': party.mean_status_shares_last_week,
        })

    factions = [{'id': 1,
                 'name': 'right_side',
                 'feeds': party_ids[14] + party_ids[17]
                },
                {'id': 2,
                 'name': 'center_side',
                 'feeds': party_ids[15] + party_ids[21] + party_ids[25],
                },
                {'id': 3,
                 'name': 'left_side',
                 'feeds': party_ids[16] + party_ids[20],
                },
                {'id': 4,
                 'name': 'arab_parties',
                 'feeds': party_ids[22] + party_ids[23] + party_ids[24],
                },
                {'id': 5,
                 'name': 'charedi_parties',
                 'feeds': party_ids[18] + party_ids[19],
                },
    ]

    factions_data = list()
    for fact in factions:
        factions_data.append({
            'faction_id': fact['id'],
            'faction_name': fact['name'],
            'num_of_weekly_statuses': engine.n_statuses_last_week(fact['feeds']),
            'mean_like_count_this_week': engine.mean_status_likes_last_week(fact['feeds']),
            'mean_comment_count_this_week': engine.mean_status_comments_last_week(fact['feeds']),
            'mean_share_count_this_week': engine.mean_status_shares_last_week(fact['feeds']),
        })

    return feeds_data, parties_data, factions_data


def statuses_data():
    week_ago, month_ago = get_times()
    week_statuses = Facebook_Status.objects.filter(published__gte=week_ago, like_count__isnull=False)
    week_statuses_build = [(status.status_id, status.feed.id, status.feed.name, status.published, status.is_deleted,
                            ';'.join([tagged_item.tag.name for tagged_item in
                                 status.tagged_items.filter(tagged_by__username='karineb')]),
                            ';'.join([tagged_item.tag.name for tagged_item in
                                 status.tagged_items.all()]),
                            status.get_link) for
                           status in week_statuses]
    field_names = ['status_id', 'feed_id', 'feed_name', 'published', 'is_deleted', 'tags_by_karine', 'tags', 'link']
    recs = np.core.records.fromrecords(week_statuses_build, names=field_names)
    week_statuses = pd.DataFrame.from_records(recs, coerce_float=True)
    return week_statuses


def build_and_send_email(data):
    date = timezone.now().date().strftime('%Y_%m_%d')

    recipients = settings.DEFAULT_WEEKLY_RECIPIENTS

    message = EmailMessage(subject='Kikar Hamedina, Weekly Report: %s' % date,
                           body='Here is the message.',
                           to=recipients)
    for datum in data:
        csvfile = StringIO.StringIO()
        data_csv = pd.DataFrame.from_dict(datum['content']).to_csv(csvfile, encoding='utf-8')
        message.attach('%s_%s.csv' % (datum['name'], date), csvfile.getvalue(), 'text/csv')
    message.send()


class Command(BaseCommand):
    help = "Calculate site stats and email it."

    def handle(self, *args, **options):
        feeds_data, parties_data, factions_data = feed_and_group_stats()
        week_statuses = statuses_data()

        all_data = [{'name': 'feeds_data',
                     'content': feeds_data},
                    {'name': 'parties_data',
                     'content': parties_data},
                    {'name': 'factions_data',
                     'content': factions_data},
                    {'name': 'week_statuses',
                     'content': week_statuses}]

        print 'Sending email..'
        build_and_send_email(all_data)
        print 'Done.'
        # return feeds_data, parties_data, factions_data, week_statuses