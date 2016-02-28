from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from tastypie import fields
from tastypie.http import HttpGone, HttpMultipleChoices

from tastypie.resources import ModelResource, Bundle
from tastypie.utils.urls import trailing_slash
from django.conf.urls import url
from facebook_feeds.models import Facebook_Status, Facebook_Feed, Tag as OldTag, User_Token, Feed_Popularity, \
    Facebook_Status_Comment, Facebook_Persona
from kikartags.models import Tag as Tag
from core.models import MEMBER_MODEL, PARTY_MODEL
from tastypie.constants import ALL, ALL_WITH_RELATIONS

from django.template.defaultfilters import urlize, truncatewords_html, linebreaks
from django.contrib.humanize.templatetags import humanize
from core.templatetags.core_extras import append_separators
from mks.models import Knesset

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


class PersonaResource(ModelResource):
    class Meta:
        queryset = Facebook_Persona.objects.all()
        resource_name = 'facebook_persona'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        filtering = {
            'object_id': ALL,
            'alt_object_id': ALL,
        }


class Facebook_FeedResource(ModelResource):
    owner = fields.ToOneField(MemberResource, attribute='owner', null=True)
    persona = fields.ForeignKey(PersonaResource, attribute='persona', null=True)

    class Meta:
        queryset = Facebook_Feed.objects.all()
        resource_name = 'facebook_feed'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        filtering = {
            'persona': ALL_WITH_RELATIONS,
            'owner': ALL_WITH_RELATIONS,
            'feed_type': ALL,
            'is_current': ['exact'],
        }

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


class Facebook_Status_CommentResource(ModelResource):
    # status = fields.ForeignKey(Facebook_StatusResource, 'parent')

    # tags = fields.ManyToManyField('CommentTagResource', 'tags')

    class Meta:
        queryset = Facebook_Status_Comment.objects.all().order_by('published')

        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        resource_name = 'facebook_status_comment'
        ordering = ['published', 'parent', 'like_count', 'comment_count']
        filtering = {
            "comment_id": ["exact"],
            "parent": ALL_WITH_RELATIONS,
            "comment_from": ["exact"],
            "content": ["exact", "startswith", "contains"],
            "published": ['exact', 'gt', 'gte', 'lt', 'lte', 'range']
        }

    def dehydrate(self, bundle):
        bundle.data['parent_status_id'] = bundle.obj.parent.status_id
        bundle.data['facebook_parent_link'] = bundle.obj.get_link
        return bundle


class Facebook_StatusResource(ModelResource):
    feed = fields.ForeignKey(Facebook_FeedResource, 'feed')
    tags = fields.ManyToManyField(TagResource, 'tags')
    comments = fields.ToManyField(to=Facebook_Status_CommentResource, attribute='facebook_status_comment_set',
                                  null=True, related_name='parent_id')

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/children%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_children'), name="api_get_children"),
        ]

    def get_children(self, request, **kwargs):
        try:
            bundle = self.build_bundle(data={'pk': kwargs['pk']}, request=request)
            obj = self.cached_obj_get(bundle=bundle, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return HttpGone()
        except MultipleObjectsReturned:
            return HttpMultipleChoices("More than one resource is found at this URI")

        child_resource = Facebook_Status_CommentResource()
        return child_resource.get_list(request, parent_id=obj.pk)

    class Meta:
        queryset = Facebook_Status.objects.all().order_by('-published')
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        resource_name = 'facebook_status'
        ordering = ['published', 'status_id', 'feed', 'like_count', 'share_count', 'comment_count']
        filtering = {
            "status_id": ["exact"],
            "feed": ALL_WITH_RELATIONS,
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
                'type': bundle.obj.attachment.type,
                'is_photo': bundle.obj.attachment.type == 'photo',
                'is_video': bundle.obj.attachment.type == 'video',
                'is_youtube_video': bundle.obj.attachment.is_youtube_video,
                'is_link': bundle.obj.attachment.type == 'link',
                'is_event': bundle.obj.attachment.type == 'event',
                'is_music': bundle.obj.attachment.type == 'music',
                'is_note': bundle.obj.attachment.type == 'note',
                'is_nonetype': not bundle.obj.attachment.type,
                'link': bundle.obj.attachment.link,
                'picture': bundle.obj.attachment.picture,
                'name': bundle.obj.attachment.name,
                'caption': bundle.obj.attachment.caption,
                'description': bundle.obj.attachment.description,
                'source': bundle.obj.attachment.source,
                'source_clean': bundle.obj.attachment.source_clean
            }
        return bundle


class CommentTagResource(ModelResource):
    statuses = fields.ManyToManyField(Facebook_Status_CommentResource, 'statuses', null=True)

    class Meta:
        queryset = Tag.objects.all()
        resource_name = 'comment_tag'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
