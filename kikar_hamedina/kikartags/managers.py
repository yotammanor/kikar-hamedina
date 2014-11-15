from django.contrib.auth.models import AnonymousUser
from django.utils import six
from django.db import models

from taggit.managers import _TaggableManager
from taggit.utils import require_instance_manager


class TagManager(models.Manager):

    def __init__(self):
        super(TagManager, self).__init__()

    def get_proper(self, *args, **kwargs):
        """
        Returns the proper form of tag.
        If the requested tag is a synonym of a proper tag, the proper version will be returned.
        Otherwise, the selected tag is returned unchanged.
        """
        selected_tag = self.get(*args, **kwargs)
        if selected_tag.proper_form_of_tag.exists():
            return selected_tag.proper_form_of_tag.first().proper_form_of_tag
        else:
            return selected_tag

    def filter_proper(self, *args, **kwargs):
        """
        Returns the queryset with proper forms of tags only.
        Receives a queryset of tags, and for each of them
        """
        selected_tags = self.filter(*args, **kwargs)
        set_of_tag_ids = set([self.get_proper(id=tag.id).id for tag in selected_tags])
        return self.filter(id__in=[tag_id for tag_id in set_of_tag_ids])

    def exclude_synonyms(self, *args, **kwargs):
        """
        Within a given queryset of tags,
        filter out tags that are synonyms of other (proper) tags.
        """
        return self.filter(*args, **kwargs).filter(proper_form_of_tag__isnull=True)

    def filter_bundle(self, *args, **kwargs):
        """
        Extends a filtered queryset of tags to
        include all proper and synonyms of those tags.
        """
        selected_tags = self.filter_proper(*args, **kwargs)
        all_ids_in_bundle = list()
        for selected_tag in selected_tags:
            all_ids_in_bundle.append(selected_tag.id)
            all_ids_in_bundle += [tag.tag.id for tag in selected_tag.synonyms.all()]
        return self.filter(id__in=set(all_ids_in_bundle))


class _KikarTaggableManager(_TaggableManager):
    def __init__(self, *args, **kwargs):
        super(_KikarTaggableManager, self).__init__(*args, **kwargs)

    @require_instance_manager
    def user_aware_add(self, user, *tags):
        """
        This function is identical to _TaggableManager.add(), but allows to set
        the tagged_by=user field. accepts user=None.

        """
        str_tags = set()
        tag_objs = set()
        for t in tags:
            if isinstance(t, self.through.tag_model()):
                tag_objs.add(t)
            elif isinstance(t, six.string_types):
                str_tags.add(t)
            else:
                raise ValueError("Cannot add {0} ({1}). Expected {2} or str.".format(
                    t, type(t), type(self.through.tag_model())))

        # If str_tags has 0 elements Django actually optimizes that to not do a
        # query.  Malcolm is very smart.
        existing = self.through.tag_model().objects.filter(
            name__in=str_tags
        )
        tag_objs.update(existing)

        for new_tag in str_tags - set(t.name for t in existing):

            tag_objs.add(self.through.tag_model().objects.create(name=new_tag))

        if user:
            tagging_user = user
        else:
            tagging_user = None

        for tag in tag_objs:
            self.through.objects.get_or_create(tag=tag, tagged_by=tagging_user,  **self._lookup_kwargs())