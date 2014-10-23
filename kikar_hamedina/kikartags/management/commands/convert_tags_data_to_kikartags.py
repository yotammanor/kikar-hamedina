from django.core.management.base import BaseCommand

from facebook_feeds.models import Tag as OldTag
from kikartags.models import Tag as Tag


class Command(BaseCommand):
    help = "My shiny new management command."

    def handle(self, *args, **options):
        Tag.objects.all().delete()

        original_tags = OldTag.objects.all()
        for old_tag in original_tags:
            print 'working on tag', old_tag.id
            new_tag, created = Tag.objects.get_or_create(name=old_tag.name)
            if created:
                print new_tag.id, 'is created!'
                new_tag.is_for_main_display = old_tag.is_for_main_display

            new_tag.save()

            for status in old_tag.statuses.all():
                status.tags.add(new_tag)

            new_tag.save()

        print Tag.objects.count()