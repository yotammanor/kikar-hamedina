from tastypie import fields
from tastypie.resources import ModelResource, Bundle
from mks.models import Knesset
from facebook_feeds.models import Facebook_Status, Facebook_Feed, Tag as OldTag, User_Token, Feed_Popularity
from kikartags.models import Tag as Tag
from planet.models import Blog
from core.models import MEMBER_MODEL, PARTY_MODEL


class MemberResource(ModelResource):
    pass


class Facebook_StatusResource(ModelResource):
    pass


def get_resource_uri(obj, field):
    if obj is None:
        return None
    resource = field.get_related_resource(obj)
    return resource.dehydrate_resource_uri(Bundle(obj=obj))


class KnessetResource(ModelResource):
    class Meta:
        queryset = Knesset.objects.all()
        resource_name = 'knesset'


class PartyResource(ModelResource):
    knesset = fields.ForeignKey(KnessetResource, 'knesset', null=True, blank=True)
    all_members = fields.ManyToManyField(MemberResource, 'all_members',  null=True, blank=True)

    class Meta:
        queryset = PARTY_MODEL.objects.all()
        resource_name = 'party'


class Facebook_FeedResource(ModelResource):
    owner = fields.ToOneField(MemberResource, attribute='owner', null=True)

    class Meta:
        queryset = Facebook_Feed.objects.all()
        resource_name = 'facebook_feed'

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

    def dehydrate_main_feed(self, bundle):
        persona = bundle.obj.facebook_persona
        if persona is not None:
            return get_resource_uri(persona.get_main_feed, self.main_feed)
        return None


class TagResource(ModelResource):
    statuses = fields.ManyToManyField(Facebook_StatusResource, 'statuses')

    class Meta:
        queryset = Tag.objects.all()
        resource_name = 'tag'


class Facebook_StatusResource(ModelResource):

    feed = fields.ForeignKey(Facebook_FeedResource, 'feed')
    tags = fields.ManyToManyField(TagResource, 'tags')

    class Meta:
        queryset = Facebook_Status.objects.all()
        resource_name = 'facebook_status'
        filtering = {
            "feed": ["exact"]
        }

    def dehydrate(self, bundle):
        bundle.data['facebook_link'] = bundle.obj.get_link

        if bundle.obj.has_attachment:
            bundle.data['attachment'] = "Attachment"
        return bundle


