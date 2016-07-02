# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook_feeds', '0007_facebook_status_comment_processed_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='facebook_status_comment',
            name='lang',
            field=models.CharField(max_length=6, null=True, blank=True),
        ),
    ]
