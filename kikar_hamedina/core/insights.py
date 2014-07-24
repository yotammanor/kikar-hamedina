from functools import wraps
from hashlib import sha1
from dateutil.relativedelta import relativedelta

import pandas
import numpy
import tastypie
from tastypie import fields
from tastypie.resources import Resource, Bundle
from mks.models import Party, Member
from facebook_feeds.models import Facebook_Status
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.utils import timezone

from api import MemberResource, PartyResource, Facebook_StatusResource


def cached(seconds=600):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
                key = sha1(repr((f.__module__, f.__name__, args, kwargs))).hexdigest()
                result = cache.get(key)
                if result is None:
                    result = f(*args, **kwargs)
                    cache.set(key, result, seconds)
                return result
        return wrapper
    return decorator

def get_times():
    now = timezone.localtime(timezone.now())
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - relativedelta(days=7)
    month_ago = today - relativedelta(months=1)
    return week_ago, month_ago

def dataframe_to_lists(dataframe):
    return [list(row) for row in dataframe.values]

def normalize(num):
    return None if numpy.isnan(num) else num


class StatsEngine(object):
    def __init__(self):
        week_ago, month_ago = get_times()
        # Note - without like_count!=NULL pandas thinks the column type is object and not number
        month_statuses = Facebook_Status.objects.filter(published__gte=month_ago, like_count__isnull=False)
        fields = ['id', 'feed', 'published', 'like_count']
        self.month_statuses = month_statuses.to_dataframe(fields=fields)
        self.week_statuses = self.month_statuses[self.month_statuses['published'] > week_ago]

    def feeds_statuses(self, statuses, feed_ids):
        return statuses[statuses['feed'].isin(feed_ids)]

    def n_statuses_last_week(self, feed_ids):
        return len(self.feeds_statuses(self.week_statuses, feed_ids))

    def n_statuses_last_month(self, feed_ids):
        return len(self.feeds_statuses(self.month_statuses, feed_ids))

    def mean_status_likes_last_week(self, feed_ids):
        return normalize(self.feeds_statuses(self.week_statuses, feed_ids)['like_count'].mean())

    def mean_status_likes_last_month(self, feed_ids):
        return normalize(self.feeds_statuses(self.month_statuses, feed_ids)['like_count'].mean())

    def popular_statuses_last_week(self, feed_ids, num=3):
        ordered = self.feeds_statuses(self.week_statuses, feed_ids).sort('like_count', ascending=False)
        return dataframe_to_lists(ordered[:num][['id', 'like_count']])

    def popular_statuses_last_month(self, feed_ids, num=3):
        ordered = self.feeds_statuses(self.month_statuses, feed_ids).sort('like_count', ascending=False)
        return dataframe_to_lists(ordered[:num][['id', 'like_count']])

    def popular_feed_last_week(self, feed_ids):
        ordered = self.feeds_statuses(self.week_statuses, feed_ids).groupby('feed')['like_count'].mean().order(ascending=False)
        return ordered.index[0] if len(ordered) > 0 else None

    def popular_feed_last_month(self, feed_ids):
        ordered = self.feeds_statuses(self.month_statuses, feed_ids).groupby('feed')['like_count'].mean().order(ascending=False)
        return ordered.index[0] if len(ordered) > 0 else None

class MemberStats(object):
    def __init__(self, member=None, engine=None):
        self.member = member
        if member is not None and engine is not None:
            try:
                persona = member.facebook_persona
                feed = persona.get_main_feed
                self.like_count = feed.get_current_fan_count
            except (ObjectDoesNotExist, AttributeError):
                pass
            else:
                self.init_stats(engine, member, persona, feed)

    def init_stats(self, engine, member, persona, feed):
        self.n_statuses_last_week = engine.n_statuses_last_week([feed.id])
        self.n_statuses_last_month = engine.n_statuses_last_month([feed.id])
        self.mean_status_likes_last_week = engine.mean_status_likes_last_week([feed.id])
        self.mean_status_likes_last_month = engine.mean_status_likes_last_month([feed.id])
        self.popular_statuses_last_week = engine.popular_statuses_last_week([feed.id])
        self.popular_statuses_last_month = engine.popular_statuses_last_month([feed.id])


class PartyStats(object):
    def __init__(self, party=None, engine=None):
        self.party = party
        if party is not None and engine is not None:
            members = party.current_members()
            feed_ids = []
            feed2member = {}
            for member in members:
                if member.facebook_persona:
                    feed_id = member.facebook_persona.get_main_feed.id
                    feed_ids.append(feed_id)
                    feed2member[feed_id] = member
            if feed_ids:
                self.init_stats(engine, feed_ids, feed2member)

    def init_stats(self, engine, feed_ids, feed2member):
        self.n_statuses_last_week = engine.n_statuses_last_week(feed_ids)
        self.n_statuses_last_month = engine.n_statuses_last_month(feed_ids)
        self.mean_status_likes_last_week = engine.mean_status_likes_last_week(feed_ids)
        self.mean_status_likes_last_month = engine.mean_status_likes_last_month(feed_ids)
        self.popular_statuses_last_week = engine.popular_statuses_last_week(feed_ids)
        self.popular_statuses_last_month = engine.popular_statuses_last_month(feed_ids)
        self.popular_member_last_month = feed2member.get(engine.popular_feed_last_month(feed_ids))
        self.popular_member_last_week = feed2member.get(engine.popular_feed_last_week(feed_ids))


class Stats(object):
    def __init__(self):
        print timezone.now(), "Reading stats data..."
        self.engine = StatsEngine()

        print timezone.now(), "Calculating stats..."
        self.member_list = [MemberStats(member, self.engine) for member in Member.objects.all()]
        self.member_dict = dict((m.member.id, m) for m in self.member_list)
        self.party_list = [PartyStats(member, self.engine) for member in Party.objects.all()]
        self.party_dict = dict((p.party.id, p) for p in self.party_list)
        print timezone.now(), "Done loading stats"

    def get_member_stats(self, member_id):
        return self.member_dict.get(member_id)

    def get_all_member_stats(self):
        return self.member_list

    def get_party_stats(self, member_id):
        return self.party_dict.get(member_id)

    def get_all_party_stats(self):
        return self.party_list


@cached(seconds=600)
def get_stats():
    return Stats()


class StatsMemberResource(Resource):
    member = fields.ForeignKey(MemberResource, 'member', null=True, blank=True)

    like_count = fields.IntegerField(attribute='like_count', null=True)
    n_statuses_last_week = fields.IntegerField(attribute='n_statuses_last_week', null=True)
    n_statuses_last_month = fields.IntegerField(attribute='n_statuses_last_month', null=True)
    mean_status_likes_last_week = fields.FloatField(attribute='mean_status_likes_last_week', null=True)
    mean_status_likes_last_month = fields.FloatField(attribute='mean_status_likes_last_month', null=True)
    popular_statuses_last_week = fields.ListField(attribute='popular_statuses_last_week', null=True)
    popular_statuses_last_month = fields.ListField(attribute='popular_statuses_last_month', null=True)

    class Meta:
        resource_name = 'insights/member'
        object_class = MemberStats

    def detail_uri_kwargs(self, bundle_or_obj):
        obj = bundle_or_obj.obj if isinstance(bundle_or_obj, Bundle) else bundle_or_obj
        return {'pk': obj.member.id }

    def get_object_list(self, request):
        return get_stats().get_all_member_stats()

    def obj_get_list(self, bundle, **kwargs):
        # TODO: filtering
        return self.get_object_list(bundle.request)

    def obj_get(self, bundle, **kwargs):
        obj = get_stats().get_member_stats(int(kwargs['pk']))
        if obj is None:
            raise tastypie.exceptions.NotFound
        return obj


class StatsPartyResource(Resource):
    party = fields.ForeignKey(PartyResource, 'party', null=True, blank=True)

    n_statuses_last_week = fields.IntegerField(attribute='n_statuses_last_week', null=True)
    n_statuses_last_month = fields.IntegerField(attribute='n_statuses_last_month', null=True)
    mean_status_likes_last_week = fields.FloatField(attribute='mean_status_likes_last_week', null=True)
    mean_status_likes_last_month = fields.FloatField(attribute='mean_status_likes_last_month', null=True)
    popular_statuses_last_week = fields.ListField(attribute='popular_statuses_last_week', null=True)
    popular_statuses_last_month = fields.ListField(attribute='popular_statuses_last_month', null=True)
    popular_member_last_week = fields.ToOneField(MemberResource, attribute='popular_member_last_week', null=True)
    popular_member_last_month = fields.ToOneField(MemberResource, attribute='popular_member_last_month', null=True)

    class Meta:
        resource_name = 'insights/party'
        object_class = PartyStats

    def detail_uri_kwargs(self, bundle_or_obj):
        obj = bundle_or_obj.obj if isinstance(bundle_or_obj, Bundle) else bundle_or_obj
        return {'pk': obj.party.id }

    def get_object_list(self, request):
        return get_stats().get_all_party_stats()

    def obj_get_list(self, bundle, **kwargs):
        # TODO: filtering
        return self.get_object_list(bundle.request)

    def obj_get(self, bundle, **kwargs):
        obj = get_stats().get_party_stats(int(kwargs['pk']))
        if obj is None:
            raise tastypie.exceptions.NotFound
        return obj
