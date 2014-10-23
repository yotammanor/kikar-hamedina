from django.contrib.auth.models import AnonymousUser
from django.utils import six

from taggit.managers import _TaggableManager
from taggit.utils import require_instance_manager


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