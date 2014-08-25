from django.utils import timezone as datetime
from haystack import indexes
from facebook_feeds.models import Facebook_Status


class FacebookStatusIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, model_attr='content')
    # feed = indexes.CharField(model_attr='feed__name')
    published = indexes.DateTimeField(model_attr='published')

    def get_model(self):
        return Facebook_Status

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(published__lte=datetime.datetime.now())