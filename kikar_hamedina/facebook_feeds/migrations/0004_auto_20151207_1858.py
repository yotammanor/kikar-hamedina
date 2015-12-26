# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook_feeds', '0003_auto_20151206_1605'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facebook_status_comment_attachment',
            name='type',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
    ]
