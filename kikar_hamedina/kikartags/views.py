"""
NOTE: This kikartags.views currently contains as-reference-only some pre-built views
from Open-Knesset, and cannot be used without major refactoring.

"""

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.core.cache import cache
from django.conf import settings

LONG_CACHE_TIME = getattr(settings, 'LONG_CACHE_TIME', 18000)  # 5 hours


import taggit

from kikartags.models import Tag, TagSynonym,  TaggedItem




#
# def calculate_cloud_from_models(*args):
#     from taggit.models import Tag
#     cloud = Tag._default_manager.cloud_for_model(args[0])
#     for model in args[1:]:
#         for tag in Tag._default_manager.cloud_for_model(model):
#             if tag in cloud:
#                 cloud[cloud.index(tag)].count+=tag.count
#             else:
#                 cloud.append(tag)
#     return taggit.utils.calculate_cloud(cloud)
#
#
# class TagList(ListView):
#     """Tags index view"""
#
#     model = Tag
#     template_name = 'auxiliary/tag_list.html'
#
#     def get_queryset(self):
#         return Tag.objects.all()
#
#     def get_context_data(self, **kwargs):
#         context = super(TagList, self).get_context_data(**kwargs)
#         tags_cloud = cache.get('tags_cloud', None)
#         if not tags_cloud:
#             tags_cloud = calculate_cloud_from_models()  # TODO: expecting args
#             tags_cloud.sort(key=lambda x:x.name)
#             cache.set('tags_cloud', tags_cloud, settings.LONG_CACHE_TIME)
#         context['tags_cloud'] = tags_cloud
#         return context
#
#
# class TagDetail(DetailView):
#     """Tags index view"""
#
#     model = Tag
#     template_name = 'auxiliary/tag_detail.html'
#     slug_field = 'name'
#
#     def create_tag_cloud(self, tag, limit=30, bills=None, votes=None,
#                          cms=None):
#         """
#         Create tag could for tag <tag>. Returns only the <limit> most tagged members
#         """
#
#         try:
#             mk_limit = int(self.request.GET.get('limit', limit))
#         except ValueError:
#             mk_limit = limit
#         if bills is None:
#             bills = TaggedItem.objects.get_by_model(Bill, tag)\
#                 .prefetch_related('proposers')
#         if votes is None:
#             votes = TaggedItem.objects.get_by_model(Vote, tag)\
#                 .prefetch_related('votes')
#         if cms is None:
#             cms = TaggedItem.objects.get_by_model(CommitteeMeeting, tag)\
#                 .prefetch_related('mks_attended')
#         mk_taggeds = [(b.proposers.all(), b.stage_date) for b in bills]
#         mk_taggeds += [(v.votes.all(), v.time.date()) for v in votes]
#         mk_taggeds += [(cm.mks_attended.all(), cm.date) for cm in cms]
#         current_k_start = Knesset.objects.current_knesset().start_date
#         d = {}
#         d_previous = {}
#         for tagged, date in mk_taggeds:
#             if date and (date > current_k_start):
#                 for p in tagged:
#                     d[p] = d.get(p, 0) + 1
#             else:  # not current knesset
#                 for p in tagged:
#                     d_previous[p] = d.get(p, 0) + 1
#         # now d is a dict: MK -> number of tagged in Bill, Vote and
#         # CommitteeMeeting in this tag, in the current knesset
#         # d_previous is similar, but for all non current knesset data
#         mks = dict(sorted(d.items(), lambda x, y: cmp(y[1], x[1]))[:mk_limit])
#         # Now only the most tagged are in the dict (up to the limit param)
#         for mk in mks:
#             mk.count = d[mk]
#         mks = taggit.utils.calculate_cloud(mks)
#
#         mks_previous = dict(sorted(d_previous.items(),
#                                    lambda x, y: cmp(y[1], x[1]))[:mk_limit])
#         for mk in mks_previous:
#             mk.count = d_previous[mk]
#         mks_previous = taggit.utils.calculate_cloud(mks_previous)
#         return mks, mks_previous
#
#     def get(self, *args, **kwargs):
#         tag = self.get_object()
#         ts = TagSynonym.objects.filter(synonym_tag=tag)
#         if len(ts) > 0:
#             proper = ts[0].tag
#             url = reverse('tag-detail', kwargs={'slug': proper.name})
#             return HttpResponsePermanentRedirect(url)
#         else:
#             return super(TagDetail, self).get(*args, **kwargs)
#
#     def get_context_data(self, **kwargs):
#         context = super(TagDetail, self).get_context_data(**kwargs)
#         tag = context['object']
#         bills_ct = ContentType.objects.get_for_model(Bill)
#         bill_ids = TaggedItem.objects.filter(
#             tag=tag,
#             content_type=bills_ct).values_list('object_id', flat=True)
#         bills = Bill.objects.filter(id__in=bill_ids)
#         context['bills'] = bills
#         votes_ct = ContentType.objects.get_for_model(Vote)
#         vote_ids = TaggedItem.objects.filter(
#             tag=tag, content_type=votes_ct).values_list('object_id', flat=True)
#         votes = Vote.objects.filter(id__in=vote_ids)
#         context['votes'] = votes
#         cm_ct = ContentType.objects.get_for_model(CommitteeMeeting)
#         cm_ids = TaggedItem.objects.filter(
#             tag=tag, content_type=cm_ct).values_list('object_id', flat=True)
#         cms = CommitteeMeeting.objects.filter(id__in=cm_ids)
#         context['cms'] = cms
#         (context['members'],
#          context['past_members']) = self.create_tag_cloud(tag)
#         return context
