from django.db import models

from slugify import slugify as default_slugify

from django.utils.translation import ugettext_lazy as _
from taggit.models import TagBase, GenericTaggedItemBase


class Tag(TagBase):
    is_for_main_display = models.BooleanField(default=True, null=False)

    def __unicode__(self):
        return self.name

    # inherit slugify from TagBase
    def slugify(self, tag, i=None):
        slug = default_slugify(tag)
        if i is not None:
            slug += "_%d" % i
        return slug

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


class TaggedItem(GenericTaggedItemBase):
    # TaggedWhatever can also extend TaggedItemBase or a combination of
    # both TaggedItemBase and GenericTaggedItemBase. GenericTaggedItemBase
    # allows using the same tag for different kinds of objects, in this
    # example Food and Drink.
    #
    # # Here is where you provide your custom Tag class.
    tag = models.ForeignKey(Tag,
                            related_name="%(app_label)s_%(class)s_items")
