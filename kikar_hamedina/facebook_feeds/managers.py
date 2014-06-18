from django.db import models
from django_pandas.managers import DataFrameManager


class Facebook_StatusManager(DataFrameManager):
    def get_queryset(self):
        return super(Facebook_StatusManager, self).get_queryset().filter(is_comment=False)