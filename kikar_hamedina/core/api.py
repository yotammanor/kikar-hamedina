from tastypie import fields
from tastypie.resources import ModelResource, Bundle
from mks.models import Knesset
from facebook_feeds.models import Facebook_Status, Facebook_Feed, Tag as OldTag, User_Token, Feed_Popularity
from kikartags.models import Tag as Tag
from core.models import MEMBER_MODEL, PARTY_MODEL
from tastypie.constants import ALL, ALL_WITH_RELATIONS

from django.template.defaultfilters import urlize, truncatewords_html, linebreaks
from django.contrib.humanize.templatetags import humanize
from core.templatetags.core_extras import append_separators

MAX_LENGTH_FOR_STATUS_CONTENT = 80


class MemberResource(ModelResource):
    pass


class Facebook_StatusResource(ModelResource):
    pass


def get_resource_uri(obj, field):
    if obj is None:
        return None
    resource = field.get_related_resource(obj)
    return resource.dehydrate_resource_uri(Bundle(obj=obj))


class KikarResource(ModelResource):
    class Meta:
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']


class KnessetResource(ModelResource):
    class Meta:
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        queryset = Knesset.objects.all()
        resource_name = 'knesset'


class PartyResource(ModelResource):
    knesset = fields.ForeignKey(KnessetResource, 'knesset', null=True, blank=True)
    all_members = fields.ManyToManyField(MemberResource, 'all_members', null=True, blank=True)

    class Meta:
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        queryset = PARTY_MODEL.objects.all()
        resource_name = 'party'


class Facebook_FeedResource(ModelResource):
    owner = fields.ToOneField(MemberResource, attribute='owner', null=True)

    class Meta:
        queryset = Facebook_Feed.objects.all()
        resource_name = 'facebook_feed'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']

    def dehydrate_owner(self, bundle):
        persona = bundle.obj.persona
        if persona is not None:
            return get_resource_uri(persona.owner, self.owner)
        return None


class MemberResource(ModelResource):
    current_party = fields.ForeignKey(PartyResource, 'current_party', null=True, blank=True)
    if hasattr(MEMBER_MODEL, 'parties'):
        parties = fields.ManyToManyField(PartyResource, 'parties')
    main_feed = fields.ToOneField(Facebook_FeedResource, attribute='main_feed', null=True)

    class Meta:
        queryset = MEMBER_MODEL.objects.all()
        resource_name = 'member'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']

    def dehydrate_main_feed(self, bundle):
        persona = bundle.obj.facebook_persona
        if persona is not None:
            return get_resource_uri(persona.get_main_feed, self.main_feed)
        return None


class TagResource(ModelResource):
    statuses = fields.ManyToManyField(Facebook_StatusResource, 'statuses', null=True)

    class Meta:
        queryset = Tag.objects.all()
        resource_name = 'tag'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']


class Facebook_StatusResource(ModelResource):
    feed = fields.ForeignKey(Facebook_FeedResource, 'feed')
    tags = fields.ManyToManyField(TagResource, 'tags')

    class Meta:
        queryset = Facebook_Status.objects.all().order_by('-published')
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        resource_name = 'facebook_status'
        ordering = ['published', 'status_id', 'feed', 'like_count', 'share_count', 'comment_count']
        filtering = {
            "status_id": ["exact"],
            "feed": ["exact"],
            "content": ["exact", "startswith", "contains"],
            "published": ['exact', 'gt', 'gte', 'lt', 'lte', 'range']
        }

    def dehydrate(self, bundle):
        bundle.data['facebook_link'] = bundle.obj.get_link
        bundle.data['member'] = bundle.obj.feed.persona.owner.name
        bundle.data['party'] = bundle.obj.feed.persona.owner.current_party.name
        bundle.data['published_str'] = humanize.naturaltime(bundle.obj.published)
        bundle.data['content_snippet'] = truncatewords_html(linebreaks(append_separators(urlize(bundle.obj.content))),
                                                            MAX_LENGTH_FOR_STATUS_CONTENT)
        if bundle.obj.has_attachment:
            bundle.data['has_attachment'] = True
            bundle.data['attachment'] = {
                'type':  bundle.obj.attachment.type,
                'link': bundle.obj.attachment.link,
                'picture': bundle.obj.attachment.picture,
                'name': bundle.obj.attachment.name,
                'caption': bundle.obj.attachment.caption,
                'description':  bundle.obj.attachment.description,
                'source': bundle.obj.attachment.source
            }
        return bundle
