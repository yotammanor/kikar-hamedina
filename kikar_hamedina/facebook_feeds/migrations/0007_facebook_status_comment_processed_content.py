# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook_feeds', '0006_auto_20160527_1407'),
    ]

    operations = [
        migrations.AddField(
            model_name='facebook_status_comment',
            name='processed_content',
            field=models.TextField(null=True, blank=True),
        ),
    ]
