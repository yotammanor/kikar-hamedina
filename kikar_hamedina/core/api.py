from tastypie import fields
from tastypie.resources import ModelResource
from mks.models import Knesset, Party, Member
from facebook_feeds.models import Facebook_Status, Facebook_Feed, Tag, User_Token, Feed_Popularity
from planet.models import Blog

class MemberResource(ModelResource): pass
class Facebook_StatusResource(ModelResource): pass


class KnessetResource(ModelResource):
	class Meta:
		queryset = Knesset.objects.all()
		resource_name = 'knesset'

class PartyResource(ModelResource):
	knesset = fields.ForeignKey(KnessetResource,'knesset',null=True, blank=True)
	all_members = fields.ManyToManyField(MemberResource, 'all_members')
	class Meta:
		queryset = Party.objects.all()
		resource_name = 'party'

class MemberResource(ModelResource):
	current_party = fields.ForeignKey(PartyResource, 'current_party', null=True, blank=True)
	parties = fields.ManyToManyField(PartyResource, 'parties')
	blog = fields.OneToOneField(Blog, 'blog', blank=True, null=True)
	class Meta:
		queryset = Member.objects.all()
		resource_name = 'member'

class Facebook_FeedResource(ModelResource):
	class Meta:
		queryset = Facebook_Feed.objects.all()
		resource_name = 'facebook_feed'

class TagResource(ModelResource):
	statuses = fields.ManyToManyField(Facebook_StatusResource,'statuses')

	class Meta:
		queryset = Tag.objects.all()
		resource_name = 'tag'

class Facebook_StatusResource(ModelResource):
	feed = fields.ForeignKey(Facebook_FeedResource, 'feed')
	tags = fields.ManyToManyField(TagResource, 'tags')
	class Meta:
		queryset = Facebook_Status.objects.all()
		resource_name = 'facebook_status'

	def dehydrate(self, bundle):
		bundle.data['facebook_link'] = bundle.obj.get_link

		if bundle.obj.has_attachment:
			bundle.data['attachment'] = "Attachment"
		return bundle


