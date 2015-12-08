# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook_feeds', '0002_auto_20151206_1455'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='facebook_status_comment_attachment',
            name='picture',
        ),
        migrations.RemoveField(
            model_name='facebook_status_comment_attachment',
            name='status',
        ),
        migrations.AddField(
            model_name='facebook_status_comment_attachment',
            name='comment',
            field=models.OneToOneField(related_name='attachment', null=True, blank=True, to='facebook_feeds.Facebook_Status_Comment'),
        ),
    ]
