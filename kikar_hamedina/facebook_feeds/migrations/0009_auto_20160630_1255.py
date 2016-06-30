# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook_feeds', '0008_facebook_status_comment_lang'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facebook_status_comment',
            name='lang',
            field=models.CharField(db_index=True, max_length=6, null=True, blank=True),
        ),
    ]
