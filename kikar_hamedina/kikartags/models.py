from django.db import models

# Create your models here.
from django.utils.translation import ugettext_lazy as _
from taggit.models import TagBase, GenericTaggedItemBase


class TaggitTag(TagBase):
    # name = models.CharField(unique=True, max_length=128)
    # statuses = models.ManyToManyField(Facebook_Status, related_name='taggit_tags')
    is_for_main_display = models.BooleanField(default=True, null=False)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


class TaggitTaggedItem(GenericTaggedItemBase):
    # TaggedWhatever can also extend TaggedItemBase or a combination of
    # both TaggedItemBase and GenericTaggedItemBase. GenericTaggedItemBase
    # allows using the same tag for different kinds of objects, in this
    # example Food and Drink.
    #
    # # Here is where you provide your custom Tag class.
    tag = models.ForeignKey(TaggitTag,
                            related_name="%(app_label)s_%(class)s_items")
